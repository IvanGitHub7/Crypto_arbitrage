import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..config import config
from ..utils.logger import logger


class DataCache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if not config.CACHE_ENABLED:
                return None

            data = self._cache.get(key)
            if data is None:
                return None

            if datetime.now() - data['timestamp'] > timedelta(seconds=config.CACHE_TTL):
                del self._cache[key]
                return None

            return data['value']

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            if not config.CACHE_ENABLED:
                return

            self._cache[key] = {
                'value': value,
                'timestamp': datetime.now()
            }

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()


cache = DataCache()