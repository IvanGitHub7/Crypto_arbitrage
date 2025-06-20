import asyncio
from typing import Callable, Any, Coroutine, TypeVar
from functools import wraps
from ..utils.logger import logger
from ..config import config

T = TypeVar('T')


def async_retry(max_retries: int = None, delay: float = None):
    """Декоратор для повторных попыток выполнения асинхронных функций"""

    def decorator(f: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(f)
        async def wrapper(*args, **kwargs) -> T:
            _max_retries = max_retries or config.RETRY_COUNT
            _delay = delay or config.RETRY_DELAY

            last_exception = None
            for attempt in range(1, _max_retries + 1):
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < _max_retries:
                        wait_time = _delay * attempt
                        logger.warning(
                            f"Attempt {attempt}/{_max_retries} failed. "
                            f"Retrying in {wait_time:.1f}s. Error: {str(e)}"
                        )
                        await asyncio.sleep(wait_time)
            raise last_exception if last_exception else Exception("Unknown error")

        return wrapper

    return decorator