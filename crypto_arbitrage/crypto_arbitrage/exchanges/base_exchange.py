import abc
import aiohttp
from typing import Dict, Optional, List
from datetime import datetime
from ..config import config
from ..utils.logger import logger
from ..utils.rate_limiter import RateLimiter
from ..utils.cache import cache
from ..utils.error_handler import async_retry


class BaseExchange(abc.ABC):
    def __init__(self, exchange_name: str):
        self.name = exchange_name
        self.config = config.get_exchange_config(exchange_name)
        self.rate_limiter = RateLimiter(self.config.get('rate_limit', 5))
        self._session: Optional[aiohttp.ClientSession] = None
        self.last_update: Dict[str, datetime] = {}

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    @async_retry()
    async def fetch_data(self, url: str, params: Optional[Dict] = None) -> Dict:
        cache_key = f"{self.name}_{url}_{str(params)}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.debug(f"Using cached data for {self.name}")
            return cached_data

        session = await self.get_session()
        async with self.rate_limiter:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_msg = f"Bad status {response.status} for {self.name}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                data = await response.json()
                await cache.set(cache_key, data)
                return data

    @abc.abstractmethod
    async def get_spot_prices(self) -> Dict[str, Dict]:
        pass

    @abc.abstractmethod
    async def get_futures_prices(self) -> Dict[str, Dict]:
        pass

    @staticmethod
    def normalize_pair(pair: str, market_type: str = 'spot') -> str:
        pair = pair.upper()
        pair = ''.join(c for c in pair if c.isalpha())

        if market_type == 'futures':
            for suffix in ['PERP', 'PERPETUAL', 'USD', 'USDT', 'SWAP']:
                if pair.endswith(suffix):
                    pair = pair[:-len(suffix)]
                    break

        for suffix in ['USDT', 'USDC', 'BUSD', 'BTC']:
            if pair.endswith(suffix):
                pair = pair[:-len(suffix)]
                break

        return pair