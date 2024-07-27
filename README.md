# async-task

_Distributed and scheduled tasks with Redis Pub/Sub_

* Create a container and define the tasks:

```python
import asyncio
from async_task import TaskManager

manager = TaskManager()


@manager.register
async def task(name: str):
    print(f'Hello {name}')


if __name__ == '__main__':
    asyncio.run(manager.run())
```

* Publish a message in the channel:

```redis
PUBLISH default '{"task":"task", "args": ["Chess"]}'
```

* The task will produce the output:

```
Hello Chess
```
