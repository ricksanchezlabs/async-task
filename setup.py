from setuptools import setup, find_packages

setup(
    name='async_task',
    version='0.0.1',
    description='Distributed and scheduled tasks with Redis Pub/Sub',
    author='Christian Gutierrez',
    packages=find_packages(),
    install_requires=[
        'aioredis==2.0.1',
    ],
)
