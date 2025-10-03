from dataclasses import dataclass
import os

try:
    # Load variables from a local .env if available
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    # Optional dependency; safe to ignore if not installed
    pass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    telegram_token: str
    phames_chat_id: str
    mission_chat_id: str
    phames_username: str = ''
    mission_thread_id: int | None = None
    phames_thread_id: int | None = None
    data_dir: str = os.environ.get('DATA_DIR', 'data')
    timezone: str = os.environ.get('TIMEZONE', 'UTC')
    auto_lock: bool = _env_bool('AUTO_LOCK', True)

    @staticmethod
    def from_env() -> 'Settings':
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not token:
            raise RuntimeError('TELEGRAM_BOT_TOKEN is required')
        phames_chat = os.environ.get('PHAMES_CHAT_ID', '')
        mission_chat = os.environ.get('MISSION_CHAT_ID', phames_chat)
        phames_username = os.environ.get('PHAMES_USERNAME', '')
        mission_thread_id = os.environ.get('MISSION_THREAD_ID')
        phames_thread_id = os.environ.get('PHAMES_THREAD_ID')
        mission_thread_parsed = int(mission_thread_id) if mission_thread_id and mission_thread_id.isdigit() else None
        phames_thread_parsed = int(phames_thread_id) if phames_thread_id and phames_thread_id.isdigit() else None
        return Settings(
            telegram_token=token,
            phames_chat_id=str(phames_chat or ''),
            mission_chat_id=str(mission_chat or ''),
            phames_username=phames_username,
            mission_thread_id=mission_thread_parsed,
            phames_thread_id=phames_thread_parsed,
        )
