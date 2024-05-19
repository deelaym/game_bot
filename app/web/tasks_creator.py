import asyncio
from asyncio import Task
from collections.abc import Awaitable
from logging import getLogger


def done_callback(result, *args) -> None:
    logger = getLogger("task")
    if result.exception():
        logger.error(result.exception())
    if args and args[0]:
        args[1]()


def create_task(coro, *args) -> Task:
    task = asyncio.create_task(coro)
    task.add_done_callback(done_callback)
    return task


def create_delayed_task(coro: Awaitable, delay: int) -> Task:
    async def _delayed_coro():
        await asyncio.sleep(delay)
        await coro

    return create_task(_delayed_coro())
