import asyncio
import time

from functools import wraps


class asyncio_cached_property:
    def __init__(self, coroutine):
        self.coroutine = coroutine
        self._cache = None
        self._lock = asyncio.Lock()
        self._cache_set = False

    def __get__(self, instance, owner):
        if instance is None:
            return self

        @wraps(self.coroutine)
        async def wrapper(*args, **kwargs):
            async with self._lock:
                if not self._cache_set:
                    self._cache = await self.coroutine(instance, *args, **kwargs)
                    self._cache_set = True
                return self._cache

        return wrapper


def test():
    async def main():
        class Example:
            @asyncio_cached_property
            async def data(self):
                print("Computing data...")
                await asyncio.sleep(0.01)  # Simulate a long-running calculation
                return time.time()

        example = Example()

        result1 = asyncio.create_task(example.data())
        result2 = asyncio.create_task(example.data())

        assert await result1 == await result2

    started_at = time.time()
    asyncio.run(main())
    assert time.time() - started_at < 0.02


if __name__ == "__main__":
    test()
