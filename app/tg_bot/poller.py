import asyncio
from asyncio import Task
from logging import getLogger


class Poller:
    def __init__(self, store) -> None:
        self.store = store
        self.logger = getLogger("poller")
        self.is_running = False
        self.poll_task: Task | None = None

    def _done_callback(self, result) -> None:
        if result.exception():
            self.logger.error(result.exception())
        if self.is_running:
            self.start()

    def start(self) -> None:
        self.is_running = True

        self.poll_task = asyncio.create_task(self.poll())
        self.poll_task.add_done_callback(self._done_callback)

    async def stop(self) -> None:
        self.is_running = False
        await self.poll_task

    async def poll(self) -> None:
        while self.is_running:
            await self.store.tg_bot.poll()
