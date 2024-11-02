import json

import redis.asyncio as redis


class RedisClient:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def pop_message(self, queue_name: str):
        data = await self.redis.blpop(queue_name, 1)
        return json.loads(data[1]) if data else None

    async def push_message(self, queue_name: str, payload: dict):
        message = json.dumps(payload)
        await self.redis.rpush(queue_name, message)

    async def close(self):
        await self.redis.aclose()
