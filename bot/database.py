"""
Database connection and operations for Codex Memory
Uses asyncpg for async Postgres operations
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import asyncpg

logger = logging.getLogger(__name__)


class Database:
    """Async Postgres database manager"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database pool created successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    async def log_event(
        self,
        user_id: str,
        kind: str,
        banner: str,
        seal: str,
        payload: Dict[str, Any]
    ) -> int:
        """Log an event to the events table"""
        query = """
            INSERT INTO events(user_id, kind, banner, seal, payload)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            event_id = await conn.fetchval(
                query,
                user_id,
                kind,
                banner,
                seal,
                payload
            )
        return event_id
    
    async def get_user_events(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent events for a user"""
        query = """
            SELECT id, ts, kind, banner, seal, payload
            FROM events
            WHERE user_id = $1
            ORDER BY ts DESC
            LIMIT $2
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id, limit)
        return [dict(row) for row in rows]
    
    async def search_events(
        self,
        user_id: str,
        search_term: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search events by banner or payload text"""
        query = """
            SELECT id, ts, kind, banner, seal, payload
            FROM events
            WHERE user_id = $1
              AND (
                banner ILIKE $2
                OR payload::text ILIKE $2
              )
            ORDER BY ts DESC
            LIMIT $3
        """
        search_pattern = f"%{search_term}%"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id, search_pattern, limit)
        return [dict(row) for row in rows]
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a user"""
        query = """
            SELECT
                (SELECT COUNT(*) FROM events WHERE user_id = $1) as event_count,
                (SELECT COUNT(*) FROM user_facts WHERE user_id = $1 AND revoked_at IS NULL) as fact_count,
                (SELECT COUNT(*) FROM memory_chunks WHERE user_id = $1) as chunk_count,
                (SELECT MAX(ts) FROM events WHERE user_id = $1 AND seal = ':: ∎') as last_sealed
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
        
        return {
            "events": row["event_count"] or 0,
            "facts": row["fact_count"] or 0,
            "chunks": row["chunk_count"] or 0,
            "last_sealed": row["last_sealed"]
        }
    
    async def store_fact(
        self,
        user_id: str,
        key: str,
        value: Dict[str, Any],
        confidence: float = 0.9
    ):
        """Store a user fact"""
        query = """
            INSERT INTO user_facts(user_id, key, value, confidence)
            VALUES ($1, $2, $3, $4)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, user_id, key, value, confidence)
    
    async def get_facts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active facts for a user"""
        query = """
            SELECT user_id, key, value, confidence, sealed_at
            FROM user_facts
            WHERE user_id = $1 AND revoked_at IS NULL
            ORDER BY sealed_at DESC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
        return [dict(row) for row in rows]
    
    async def store_memory_chunk(
        self,
        user_id: str,
        banner: str,
        text: str,
        tags: List[str],
        embedding: Optional[List[float]] = None
    ) -> int:
        """Store a memory chunk with optional embedding"""
        query = """
            INSERT INTO memory_chunks(user_id, banner, text, tags, embedding)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            chunk_id = await conn.fetchval(
                query,
                user_id,
                banner,
                text,
                tags,
                embedding
            )
        return chunk_id
