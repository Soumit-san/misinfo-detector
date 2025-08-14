# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    newsapi_key: str = Field(..., env="NEWSAPI_KEY")
    google_fact_check_api_key: str = Field(..., env="GOOGLE_FACT_CHECK_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
