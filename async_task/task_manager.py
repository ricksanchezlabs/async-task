import asyncio
import signal
import traceback

from async_task import RedisClient, logger, settings


class TaskManager:
    _tasks = {}

    def __init__(self, queue_name: str = 'default'):
        self.queue_name = queue_name
        self.redis = RedisClient(settings.REDIS_HOST)

        self.loop = asyncio.get_event_loop()

        self.stop = False

        for s in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(s, lambda _s=s: asyncio.create_task(self._gracefully_stop(_s)))

    def register(self, func):
        self._tasks[func.__name__] = func
        return func

    async def _listen_to_queue(self):
        while not self.stop:
            if not (payload := await self.redis.pop_message(self.queue_name)):
                continue

            task = payload.get('task')
            if fn := self._tasks.get(task):
                args = payload.get('args', ())
                kwargs = payload.get('kwargs', {})
                # noinspection PyBroadException
                try:
                    logger.info(f'Calling {task=} with {args=} and {kwargs=}')
                    # noinspection PyAsyncCall
                    asyncio.create_task(fn(*args, **kwargs))
                except Exception:
                    logger.error('Error calling task\n' + traceback.format_exc())

    def run(self):
        self.loop.create_task(self._listen_to_queue())
        logger.info(f'Listening to queue {self.queue_name}...')
        self.loop.run_forever()
        self.loop.close()

    async def _close(self):
        await self.redis.close()

    async def _gracefully_stop(self, _signal):
        self.stop = True

        logger.info(f'Received signal {_signal}, gracefully stopping')
        try:
            if running_tasks := [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]:
                await asyncio.wait(running_tasks, timeout=settings.GRACEFUL_STOP_TIMEOUT)

            await self._close()
        except Exception as e:
            logger.exception(f'Exception occurred while gracefully stopping {e=}')
        finally:
            self.loop.stop()
