import json

import aiofiles
import google.cloud.texttospeech as tts
import litellm
from fastapi import HTTPException
from google.api_core import exceptions as google_exceptions
from google.oauth2 import service_account
from openai import OpenAIError

from app.utils.ai_logger import logger as logger
from config import settings


class SpeechConversionService:

    async def text_to_speech(
        self, text: str, output_file: str, voice_name: str, step_name: str
    ):
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_service_credenitals_file_path
        )

        client = tts.TextToSpeechAsyncClient(credentials=credentials)

        language_code = "en-US"

        voice_params = tts.VoiceSelectionParams(
            language_code=language_code, name=voice_name
        )
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
        text_input = tts.SynthesisInput(text=text)

        try:
            response = await client.synthesize_speech(
                input=text_input,
                voice=voice_params,
                audio_config=audio_config,
            )
        except google_exceptions.Unauthenticated as e:
            logger.error(
                f"{step_name} Error synthesizing ai's voice: Please verify that your service credentials are correct and have the required permissions."
            )
            raise HTTPException(status_code=500, detail=str(e))

        async with aiofiles.open(output_file, "wb") as f:
            logger.debug(
                f"{step_name} Writing AI response audio content to {output_file}"
            )
            await f.write(response.audio_content)

        return output_file

    async def speech_to_text(self, input_file: str, step_name: str):
        async with aiofiles.open(input_file, "rb") as f:
            content = await f.read()

        try:
            transcript = await litellm.atranscription(
                model=settings.transcript_model_name,
                file=(input_file, content),
                temperature=0,
                response_format="verbose_json",
            )

            user_message = transcript.text.strip()
            logger.debug(f"{step_name}: {json.dumps(transcript.json(), indent=4)}")

        except OpenAIError as e:
            logger.error(f"{step_name} Error transcribing user's voice: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        return user_message


speech_service = SpeechConversionService()
