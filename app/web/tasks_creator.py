import asyncio
from asyncio import Task
from collections.abc import Awaitable
from logging import getLogger

logger = getLogger("task")


def done_callback(result) -> None:
    if result.exception():
        logger.error(result.exception())


def done_callback_for_polling(result, is_running, start):
    if result.exception():
        logger.error(result.exception())
    if is_running:
        start()


def create_task(coro, *args) -> Task:
    task = asyncio.create_task(coro)
    if args:
        task.add_done_callback(done_callback_for_polling)
        return task
    task.add_done_callback(done_callback)
    return task


def create_delayed_task(coro: Awaitable, delay: int) -> Task:
    async def _delayed_coro():
        await asyncio.sleep(delay)
        await coro

    return create_task(_delayed_coro())
