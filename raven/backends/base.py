from abc import ABC, abstractmethod
from typing import List

from raven.config import Settings
from raven.memory import ChatMessage


class ChatBackend(ABC):
    """Abstract backend interface for generating replies."""

    @abstractmethod
    async def generate_reply(
        self,
        chat_id: int,
        history: List[ChatMessage],
        user_message: str,
        settings: Settings,
    ) -> str:
        raise NotImplementedError
