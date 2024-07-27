import asyncio
import json
import traceback
from json import JSONDecodeError

import async_timeout
from aioredis.client import PubSub

from async_task import RedisClient, logger, settings


class TaskManager:
    _tasks = {}

    def __init__(self, channel_name: str = 'default'):
        self.channel_name = channel_name
        self.redis = RedisClient(settings.REDIS_HOST)

    def register(self, func):
        self._tasks[func.__name__] = func

    async def send_task(self, channel_name: str, task: str, args: list, kwargs: dict):
        payload = dict(
            task=task,
            args=args,
            kwargs=kwargs
        )
        await self.redis.publish_message(channel_name, payload)

    async def process_message(self, channel: PubSub):
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await channel.get_message(ignore_subscribe_messages=True)
                    if message is not None and message.get('channel') == self.channel_name:
                        try:
                            payload = json.loads(message.get('data'))
                        except JSONDecodeError:
                            pass
                        else:
                            task = payload.get('task')
                            args = payload.get('args', ())
                            kwargs = payload.get('kwargs', {})
                            if task in self._tasks:
                                fn = self._tasks.get(task)
                                logger.info(f'Calling {task=} with {args=} and {kwargs=}')
                                # noinspection PyBroadException
                                try:
                                    # noinspection PyAsyncCall
                                    asyncio.create_task(fn(*args, **kwargs))
                                except Exception:
                                    logger.error('Error calling task\n' + traceback.format_exc())
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass

    async def run(self):
        logger.info(f'Subscribing to channel {self.channel_name}...')
        pubsub = await self.redis.subscribe_channel(self.channel_name)
        await asyncio.create_task(self.process_message(pubsub))

    async def close(self):
        await self.redis.close()
