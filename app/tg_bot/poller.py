from asyncio import Task
from logging import getLogger

from app.web.tasks_creator import create_task


class Poller:
    def __init__(self, store) -> None:
        self.store = store
        self.logger = getLogger("poller")
        self.is_running = False
        self.poll_task: Task | None = None

    def start(self) -> None:
        self.is_running = True
        self.poll_task = create_task(self.poll(), self.is_running, self.start)

    async def stop(self) -> None:
        self.is_running = False
        await self.poll_task

    async def poll(self) -> None:
        while self.is_running:
            await self.store.tg_bot.poll()
