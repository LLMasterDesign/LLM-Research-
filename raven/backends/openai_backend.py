import asyncio
from typing import List

from openai import AsyncOpenAI

from raven.backends.base import ChatBackend
from raven.config import Settings
from raven.memory import ChatMessage


class OpenAIBackend(ChatBackend):
    def __init__(self, client: AsyncOpenAI | None = None):
        self.client = client

    async def generate_reply(
        self,
        chat_id: int,
        history: List[ChatMessage],
        user_message: str,
        settings: Settings,
    ) -> str:
        if not settings.openai_api_key:
            return "OpenAI API key is not configured. Set OPENAI_API_KEY."

        client = self.client or AsyncOpenAI(api_key=settings.openai_api_key)
        messages = [
            {"role": "system", "content": settings.system_prompt},
        ]
        for m in history[-20:]:
            messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": user_message})

        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.2,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"OpenAI error: {e}"
