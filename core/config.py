from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # API Keys
    GOOGLE_API_KEY: str
    WEATHER_API_KEY: str
    EXCHANGE_RATES_API_KEY: str
    RAPIDAPI_KEY: str
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    # LLM Configuration
    MODEL_PROVIDER: str = "google"
    GOOGLE_MODEL_NAME: str = "gemini-2.0-flash"
    OPENAI_MODEL_NAME: str = "gpt-4o"
    GROQ_MODEL_NAME: str = "llama3-70b-8192"

    # Database
    DATABASE_URL: str = "sqlite:///trip_planner.db"


settings = Settings()
