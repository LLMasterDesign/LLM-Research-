import os
from dataclasses import dataclass
from typing import Optional

try:
    # Optional, do not fail if missing
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass


@dataclass
class Settings:
    telegram_bot_token: Optional[str] = None
    allowed_user_ids: Optional[str] = None  # comma-separated integers

    default_backend: str = os.getenv("DEFAULT_BACKEND", "openai")

    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    system_prompt: str = os.getenv(
        "SYSTEM_PROMPT",
        "You are Raven, a precise, helpful coding assistant integrated with my development workflow.",
    )

    # n8n relay
    n8n_webhook_url: Optional[str] = os.getenv("N8N_WEBHOOK_URL")

    # Generic relay
    relay_url: Optional[str] = os.getenv("RELAY_URL")

    # Runtime
    db_path: str = os.getenv("DB_PATH", "./data/raven.db")
    use_webhook: bool = os.getenv("USE_WEBHOOK", "false").lower() in {"1", "true", "yes"}
    webhook_url: Optional[str] = os.getenv("WEBHOOK_URL")
    port: int = int(os.getenv("PORT", "8080"))


def load_settings() -> Settings:
    settings = Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        allowed_user_ids=os.getenv("ALLOWED_USER_IDS"),
    )
    return settings
