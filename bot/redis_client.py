"""
Redis client for ephemeral session caching
"""
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisCache:
    """Async Redis client for session caching"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def cache_message(
        self,
        user_id: str,
        text: str,
        banner: str,
        has_seal: bool,
        ttl: int = 3600
    ):
        """Cache a message in Redis with TTL"""
        key = f"msg:{user_id}:{datetime.utcnow().timestamp()}"
        data = {
            "text": text,
            "banner": banner,
            "has_seal": has_seal,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.client.setex(
            key,
            ttl,
            json.dumps(data)
        )
    
    async def get_recent_messages(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent cached messages for a user"""
        pattern = f"msg:{user_id}:*"
        keys = []
        async for key in self.client.scan_iter(match=pattern, count=100):
            keys.append(key)
        
        # Sort by timestamp (in key) and take last N
        keys.sort(reverse=True)
        keys = keys[:limit]
        
        messages = []
        for key in keys:
            data = await self.client.get(key)
            if data:
                messages.append(json.loads(data))
        
        return messages
    
    async def set_user_context(
        self,
        user_id: str,
        context: Dict[str, Any],
        ttl: int = 7200
    ):
        """Set user context (ephemeral state)"""
        key = f"ctx:{user_id}"
        await self.client.setex(
            key,
            ttl,
            json.dumps(context)
        )
    
    async def get_user_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user context"""
        key = f"ctx:{user_id}"
        data = await self.client.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def increment_counter(self, key: str, ttl: int = 86400) -> int:
        """Increment a counter with TTL"""
        value = await self.client.incr(key)
        if value == 1:  # First increment, set TTL
            await self.client.expire(key, ttl)
        return value
    
    async def get_stats(self, user_id: str) -> Dict[str, int]:
        """Get cached stats for a user"""
        stats = {}
        
        # Count messages
        pattern = f"msg:{user_id}:*"
        count = 0
        async for _ in self.client.scan_iter(match=pattern, count=100):
            count += 1
        stats["cached_messages"] = count
        
        # Get daily message count
        today = datetime.utcnow().strftime("%Y-%m-%d")
        daily_key = f"daily:{user_id}:{today}"
        stats["messages_today"] = int(await self.client.get(daily_key) or 0)
        
        return stats
