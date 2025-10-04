"""
Memory Manager - orchestrates database and cache operations
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages memory operations across Postgres and Redis"""
    
    def __init__(self, db, redis_cache):
        self.db = db
        self.redis = redis_cache
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        # Get DB stats
        db_stats = await self.db.get_user_stats(user_id)
        
        # Get Redis stats
        redis_stats = await self.redis.get_stats(user_id)
        
        # Combine
        return {
            "events": db_stats["events"],
            "facts": db_stats["facts"],
            "chunks": db_stats["chunks"],
            "last_sealed": db_stats["last_sealed"],
            "cached_messages": redis_stats.get("cached_messages", 0),
            "messages_today": redis_stats.get("messages_today", 0)
        }
    
    async def search_events(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search user events"""
        return await self.db.search_events(user_id, query, limit)
    
    async def store_sealed_memory(
        self,
        user_id: str,
        banner: str,
        text: str,
        tags: Optional[List[str]] = None
    ):
        """Store a sealed memory (for future embedding)"""
        if tags is None:
            tags = self._extract_tags(text)
        
        # Store in DB
        chunk_id = await self.db.store_memory_chunk(
            user_id=user_id,
            banner=banner,
            text=text,
            tags=tags
        )
        
        logger.info(f"Stored memory chunk {chunk_id} for user {user_id}")
        return chunk_id
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from text (simple implementation)"""
        # Look for hashtags
        import re
        tags = re.findall(r'#(\w+)', text)
        
        # Add special markers
        if "⟦⎊⟧" in text:
            tags.append("ritual")
        if "∎" in text:
            tags.append("sealed")
        
        return tags[:10]  # Limit to 10 tags
    
    async def get_context(self, user_id: str) -> Dict[str, Any]:
        """Get current user context"""
        # Try Redis first
        ctx = await self.redis.get_user_context(user_id)
        if ctx:
            return ctx
        
        # Fallback: build from recent events
        events = await self.db.get_user_events(user_id, limit=5)
        facts = await self.db.get_facts(user_id)
        
        context = {
            "recent_events": len(events),
            "active_facts": len(facts),
            "initialized": datetime.utcnow().isoformat()
        }
        
        # Cache it
        await self.redis.set_user_context(user_id, context)
        
        return context
