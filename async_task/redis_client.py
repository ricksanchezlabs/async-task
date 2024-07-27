import json

import aioredis


class RedisClient:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)

    async def subscribe_channel(self, channel_name):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel_name)
        return pubsub

    async def publish_message(self, channel: str, payload: dict):
        message = json.dumps(payload)
        await self.redis.publish(channel, message)

    async def close(self):
        await self.redis.close()
