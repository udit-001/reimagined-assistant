import json
import logging
import os

import aiofiles
import google.cloud.texttospeech as tts
import litellm
from fastapi import HTTPException
from google.oauth2 import service_account
from openai import OpenAIError

from config import settings

from ..utils.ai_logger import logger as ai_logger
from .persona import Persona
from .prompts import prompt_manager

logger = ai_logger
logger.setLevel(logging.DEBUG if settings.debug_mode else logging.INFO)


class Chatbot:
    def __init__(self, persona: Persona, user_id: str):
        self.memory = []
        self.summary_threshold = 10
        self.current_summary = ""
        self.persona = persona
        self.user_id = user_id
        self.system_prompt = prompt_manager.get_prompt(persona.name)

    def __repr__(self) -> str:
        return f"<Chatbot ({self.persona.name}): {self.user_id}>"

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def reset_memory(self):
        self.memory = []

    def get_prompt(self):
        return (
            f"\n{self.current_summary}".join(self.memory[-(self.summary_threshold) :])
            + f"\nAI: "
        )

    async def respond(self, message):
        self.memory.append(f"HUMAN: {message}")

        if len(self.memory) > self.summary_threshold:
            await self.summarize()

        ai_response = await self.__generate_llm_response()
        self.memory.append(f"AI: {ai_response}")

        return ai_response

    async def voice_respond(self, input_filename: str):
        user_message = await self.__speech_to_text(input_filename)

        if os.path.exists(input_filename):
            os.remove(input_filename)

        ai_response = await self.respond(user_message)
        output_filename = await self.__text_to_speech(ai_response)
        return output_filename

    async def __speech_to_text(self, input_filename: str):
        async with aiofiles.open(input_filename, "rb") as f:
            content = await f.read()

        try:
            transcript = await litellm.atranscription(
                model=settings.transcript_model_name,
                file=(input_filename, content),
                temperature=0,
                response_format="verbose_json",
            )

            user_message = transcript.text.strip()
            logger.debug(
                f"Transcription Step: {json.dumps(transcript.json(), indent=4)}"
            )
            logger.debug(f"User ({self.user_id}): {user_message}")

            if any([i["no_speech_prob"] > 0.05 for i in transcript.segments]):
                print("Silent speech detected")
                return ""
        except OpenAIError as e:
            logger.error(f"Error transcribing user's voice: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        return user_message

    async def __text_to_speech(self, message: str):
        filename = f"{settings.media_path}/output-{self.user_id}.wav"

        credentials = service_account.Credentials.from_service_account_file(
            settings.google_service_credenitals_file_path
        )
        client = tts.TextToSpeechAsyncClient(credentials=credentials)

        language_code = "en-US"

        voice_params = tts.VoiceSelectionParams(
            language_code=language_code, name=self.persona.voice
        )
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
        text_input = tts.SynthesisInput(text=message)

        logger.debug(f"Speech Synthesis Step running...")
        response = await client.synthesize_speech(
            input=text_input,
            voice=voice_params,
            audio_config=audio_config,
        )

        async with aiofiles.open(filename, "wb") as f:
            ai_logger.debug(f"Writing AI response audio content to {filename}")
            await f.write(response.audio_content)

        return filename

    async def __generate_llm_response(self):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.get_prompt()},
        ]

        try:
            stream = await litellm.acompletion(
                model=settings.llm_model_name, messages=messages, stream=True
            )

            chunks = []
            async for chunk in stream:
                chunks.append(chunk)

            streamed_response = litellm.stream_chunk_builder(chunks, messages=messages)
        except OpenAIError as e:
            logger.error(f"Error generating LLM response: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        ai_message = streamed_response.choices[0].message.content

        logger.debug(
            f"LLM Response Step: {json.dumps(streamed_response.json(), indent=4)}"
        )
        logger.debug(f"AI({self.persona.name}) - {ai_message}")
        return ai_message

    async def summarize(self):
        prompt = prompt_manager.get_prompt("summarization_prompt", {"context": "\n".join(self.memory)})
        messages = [
            {"role": "system", "content": prompt},
        ]

        try:
            stream = await litellm.acompletion(
                model=settings.llm_model_name, messages=messages, stream=True
            )

            chunks = []
            async for chunk in stream:
                chunks.append(chunk)

            streamed_response = litellm.stream_chunk_builder(chunks, messages=messages)

            self.current_summary = streamed_response.choices[0].message.content
            logger.debug(
                f"Conversation exceeded summary threshold, summarizing previous messages, generated summary: {self.current_summary}"
            )
        except OpenAIError as e:
            logger.error(f"Error summarizing conversation: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        self.memory = self.memory[-(self.summary_threshold) :]
