from enum import Enum

from pydantic import DirectoryPath, FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict


class GroqCompletionModelEnum(str, Enum):
    LLAMA_8B = "groq/llama-3.1-8b-instant"
    LLAMA_70B = "groq/llama-3.1-70b-versatile"
    LLAMA_3_8B = "groq/llama3-8b-8192"
    LLAMA_3_70B = "groq/llama3-70b-8192"
    LLAMA_2 = "groq/llama2-70b-4096"
    MIXTRAL_8X7B = "groq/mixtral-8x7b-32768"
    GEMMA_7B = "groq/gemma-7b-it"


class GroqTranscriptionModelEnum(str, Enum):
    DISTILL_WHISPER = "groq/distil-whisper-large-v3-en"
    WHISPER_LARGE = "groq/whisper-large-v3"


class Settings(BaseSettings):
    groq_api_key: str
    debug_mode: bool = False
    google_service_credenitals_file_path: FilePath
    media_path: DirectoryPath = "media"
    llm_model_name: GroqCompletionModelEnum = GroqCompletionModelEnum.LLAMA_3_8B
    transcript_model_name: GroqTranscriptionModelEnum = (
        GroqTranscriptionModelEnum.DISTILL_WHISPER
    )

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
