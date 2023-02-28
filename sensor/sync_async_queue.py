import asyncio
from queue import Queue, Empty


class SyncToAsyncQueue(Queue):
    def __init__(self, size: int = 0, timeout: float = 0.02):
        super().__init__(size)
        self._timeout = timeout

    async def aget(self):
        while True:
            try:
                return self.get_nowait()
            except Empty:
                await asyncio.sleep(self._timeout)
