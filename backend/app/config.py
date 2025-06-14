from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, ValidationError
from dotenv import load_dotenv
import os

# Load .env file from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

class Settings(BaseSettings):
    VAPI_API_KEY: str
    WEBHOOK_SECRET: str
    PUBLIC_URL: Optional[AnyHttpUrl] = "http://127.0.0.1:8000"
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    OPENAI_API_KEY: Optional[str] = None
    SPORT_TYPE: str = "football"  # Added to toggle between football and cricket

    class Config:
        case_sensitive = False

try:
    settings = Settings()
except ValidationError as exc:
    missing = ", ".join(
        e["loc"][0] for e in exc.errors() if e["type"].startswith("value_error.missing")
    )
    raise RuntimeError(
        f"Required environment variables are missing: {missing}. "
        "Create a .env file or export them in your shell."
    )