from pydantic import FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    debug_mode: bool = False
    google_service_credenitals_file_path: FilePath

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
