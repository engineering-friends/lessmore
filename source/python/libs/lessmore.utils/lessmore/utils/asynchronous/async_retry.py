import asyncio

from typing import Callable, Optional, Type

from loguru import logger


def async_retry(
    tries: Optional[int] = None,
    delay: int = 1,
    condition: Callable = lambda e: True,
):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                if attempt > 0:
                    logger.debug("Retry attempt", func_name=func.__name__, attempt=attempt)

                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if not condition(e):
                        raise

                    attempt += 1
                    if tries is not None and attempt >= tries:
                        raise
                    await asyncio.sleep(delay)

                    logger.warning(f"Retry attempt #{attempt} after exception: {e}")

        return wrapper

    return decorator


def test():
    @async_retry(tries=3, delay=1, condition=lambda e: isinstance(e, ValueError))
    async def test_func():
        raise ValueError("Test exception")

    asyncio.run(test_func())


if __name__ == "__main__":
    test()
