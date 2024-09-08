import logging
import os

from fastapi.concurrency import run_in_threadpool
from silero_vad import get_speech_timestamps, load_silero_vad, read_audio

from config import settings

from ..utils.ai_logger import logger as ai_logger
from .ai.llm import llm_service
from .ai.speech_conversion_service import speech_service
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
        self.system_prompt = prompt_manager.get_prompt(
            "system_prompt", {"persona": persona.name}
        )

    def __repr__(self) -> str:
        return f"<Chatbot ({self.persona.name}): {self.user_id}>"

    def __is_silent_audio(self, filename):
        ai_logger.debug("Checking user's audio for silence using Silero VAD")
        model = load_silero_vad()
        wav = read_audio(filename)
        speech_timestamps = get_speech_timestamps(wav, model)

        if len(speech_timestamps) > 0:
            return False

        ai_logger.debug(
            "No speech detected in user's audio, skipping transcription step"
        )
        return True

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def reset_memory(self):
        self.memory = []

    def get_prompt(self):
        return (
            f"\n{self.current_summary}".join(self.memory[-(self.summary_threshold) :])
            + f"\nAI: "
        )

    async def __generate_ai_response(self):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.get_prompt()},
        ]
        ai_message = await llm_service.chat_completion(
            messages, step_name="LLM Response Step"
        )
        logger.debug(f"AI({self.persona.name}) - {ai_message}")
        return ai_message

    async def summarize(self):
        prompt = prompt_manager.get_prompt(
            "summarization_prompt", {"context": "\n".join(self.memory)}
        )
        messages = [
            {"role": "system", "content": prompt},
        ]

        logger.debug(
            f"Conversation exceeded summary threshold, summarizing previous messages"
        )

        self.current_summary = await llm_service.chat_completion(
            messages, step_name="LLM Response Step (Summarization)"
        )

        self.memory = self.memory[-(self.summary_threshold) :]

    async def __check_for_silence(self, input_file):
        response = await run_in_threadpool(self.__is_silent_audio, input_file)
        return response

    async def __silent_speech_response(self):
        messages = [
            {
                "role": "system",
                "content": prompt_manager.get_prompt("silent_prompt"),
            }
        ]

        ai_message = await llm_service.chat_completion(
            messages, step_name="LLM Response Step (Silent Speech)"
        )
        self.memory.append(f"AI: {ai_message}")
        logger.debug(f"AI({self.persona.name}) - {ai_message}")
        return ai_message

    async def respond(self, message):
        self.memory.append(f"HUMAN: {message}")

        if len(self.memory) > self.summary_threshold:
            await self.summarize()

        if message == "":
            ai_response = await self.__silent_speech_response()
        else:
            ai_response = await self.__generate_ai_response()

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

        if await self.__check_for_silence(input_filename):
            return ""

        user_message = await speech_service.speech_to_text(
            input_filename, step_name="Transcription Service"
        )

        logger.debug(f"User ({self.user_id}): {user_message}")

        return user_message

    async def __text_to_speech(self, message: str):
        filename = f"{settings.media_path}/output-{self.user_id}.wav"

        logger.debug(f"Speech Synthesis Step running...")
        await speech_service.text_to_speech(message, filename, self.persona.voice)

        return filename
