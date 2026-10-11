import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    backend_host: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    frontend_port: int = int(os.getenv("FRONTEND_PORT", "8501"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    memory_store_path: str = os.getenv("MEMORY_STORE_PATH", "./memory_store")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
