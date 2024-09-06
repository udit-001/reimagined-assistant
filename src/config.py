from enum import Enum

from pydantic import DirectoryPath, FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict


class GroqCompletionModelEnum(str, Enum):
    llama_8b = "groq/llama-3.1-8b-instant"
    llama_70b = "groq/llama-3.1-70b-versatile"
    llama_3_8b = "groq/llama3-8b-8192"
    llama_3_70b = "groq/llama3-70b-8192"
    llama_2 = "groq/llama2-70b-4096"
    mixtral_8x7b = "groq/mixtral-8x7b-32768"
    gemma_7b = "groq/gemma-7b-it"


class GroqTranscriptionModelEnum(str, Enum):
    distill_whisper = "groq/distil-whisper-large-v3-en"
    whisper_large = "groq/whisper-large-v3"


class Settings(BaseSettings):
    groq_api_key: str
    debug_mode: bool = False
    google_service_credenitals_file_path: FilePath
    media_path: DirectoryPath = "media"
    llm_model_name: GroqCompletionModelEnum = GroqCompletionModelEnum.llama_3_8b
    transcript_model_name: GroqTranscriptionModelEnum = (
        GroqTranscriptionModelEnum.distill_whisper
    )

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
