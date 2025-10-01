from typing import List

import httpx

from raven.backends.base import ChatBackend
from raven.config import Settings
from raven.memory import ChatMessage


class RelayBackend(ChatBackend):
    def __init__(self, client: httpx.AsyncClient | None = None):
        self.client = client or httpx.AsyncClient(timeout=60)

    async def generate_reply(
        self,
        chat_id: int,
        history: List[ChatMessage],
        user_message: str,
        settings: Settings,
    ) -> str:
        if not settings.relay_url:
            return "Relay URL is not configured. Set RELAY_URL."

        payload = {
            "chat_id": chat_id,
            "history": [m.__dict__ for m in history[-20:]],
            "message": user_message,
        }
        try:
            async with self.client as client:
                resp = await client.post(settings.relay_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, dict) and "reply" in data:
                    return str(data["reply"])
                return str(data)
        except Exception as e:
            return f"Relay error: {e}"
