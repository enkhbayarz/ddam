from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    app_name: str = "Persona Chat API"
    cors_origins: list[str] = ["http://localhost:5173"]
    personas_path: Path = BACKEND_DIR / "data" / "personas.json"
    conversations_path: Path = BACKEND_DIR / "data" / "conversations.json"

    ai_gateway_api_key: SecretStr | None = None
    ai_gateway_base_url: str = "https://ai-gateway.vercel.sh/v1"
    ai_gateway_model: str = "deepseek/deepseek-v4-flash"


@lru_cache
def get_settings() -> Settings:
    return Settings()
