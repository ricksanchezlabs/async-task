from setuptools import setup, find_packages

setup(
    name='async_task',
    version='0.0.2',
    description='Distributed and scheduled tasks with Redis Pub/Sub',
    author='Christian Gutierrez',
    packages=find_packages(),
    install_requires=[
        'redis==5.2.0',
    ],
)
