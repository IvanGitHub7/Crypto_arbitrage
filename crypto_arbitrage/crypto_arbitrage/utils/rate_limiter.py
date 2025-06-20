import asyncio
from typing import Optional
from ..config import config
from ..utils.logger import logger


class RateLimiter:
    def __init__(self, max_rate: float = 5):
        self.max_rate = max_rate
        self.time_period = 1.0  # 1 секунда
        self._semaphore = asyncio.Semaphore(max_rate)
        self._last_call_time: Optional[float] = None

    async def __aenter__(self):
        await self._semaphore.acquire()
        now = asyncio.get_event_loop().time()

        if self._last_call_time is not None:
            elapsed = now - self._last_call_time
            wait_time = max(0.0, self.time_period / self.max_rate - elapsed)
            if wait_time > 0:
                logger.debug(f"Rate limiting - waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

        self._last_call_time = asyncio.get_event_loop().time()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._semaphore.release()