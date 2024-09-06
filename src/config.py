from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    debug_mode: bool = False
    speech_to_text_model: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
