import aiosqlite
from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple
import os
import asyncio

Role = Literal["system", "user", "assistant"]


@dataclass
class ChatMessage:
    role: Role
    content: str


class MemoryStore:
    def __init__(self, db_path: str):
        self._db_path = db_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init_lock = asyncio.Lock()

    async def initialize(self) -> None:
        async with self._init_lock:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS settings (
                        chat_id INTEGER PRIMARY KEY,
                        backend TEXT
                    )
                    """
                )
                await db.commit()

    async def append_message(self, chat_id: int, role: Role, content: str) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                (chat_id, role, content),
            )
            await db.commit()

    async def get_history(self, chat_id: int, limit: int = 20) -> List[ChatMessage]:
        async with aiosqlite.connect(self._db_path) as db:
            # Get last N messages for the chat in chronological order
            async with db.execute(
                "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                (chat_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
        rows.reverse()
        return [ChatMessage(role=row[0], content=row[1]) for row in rows]

    async def clear_history(self, chat_id: int) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            await db.commit()

    async def get_backend(self, chat_id: int) -> Optional[str]:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT backend FROM settings WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
        return row[0] if row and row[0] else None

    async def set_backend(self, chat_id: int, backend: str) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "INSERT INTO settings (chat_id, backend) VALUES (?, ?) ON CONFLICT(chat_id) DO UPDATE SET backend = excluded.backend",
                (chat_id, backend),
            )
            await db.commit()
