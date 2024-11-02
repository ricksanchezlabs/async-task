import os

GRACEFUL_STOP_TIMEOUT = float(os.getenv('GRACEFUL_STOP_TIMEOUT', 5))
REDIS_HOST = os.getenv('REDIS_HOST', 'redis://localhost')
