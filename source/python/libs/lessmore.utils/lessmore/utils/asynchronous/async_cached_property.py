import asyncio
import time

from functools import wraps


class async_cached_property:
    def __init__(self, coroutine):
        self.coroutine = coroutine

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # Get or create cache and lock attributes on the instance
        cache_attr = f"_{self.coroutine.__name__}_cache"
        lock_attr = f"_{self.coroutine.__name__}_lock"
        cache_set_attr = f"_{self.coroutine.__name__}_cache_set"

        if not hasattr(instance, cache_attr):
            setattr(instance, cache_attr, None)
            setattr(instance, lock_attr, asyncio.Lock())
            setattr(instance, cache_set_attr, False)

        @wraps(self.coroutine)
        async def wrapper(*args, **kwargs):
            async with getattr(instance, lock_attr):
                if not getattr(instance, cache_set_attr):
                    print("Running", self.coroutine.__name__)
                    result = await self.coroutine(instance, *args, **kwargs)
                    setattr(instance, cache_attr, result)
                    setattr(instance, cache_set_attr, True)
                return getattr(instance, cache_attr)

        return wrapper()


def test():
    async def main():
        class Example:
            @async_cached_property
            async def data(self):
                print("Computing data...")
                await asyncio.sleep(0.01)  # Simulate a long-running calculation
                return time.time()

        example1 = Example()
        example2 = Example()

        result1a = asyncio.create_task(example1.data)
        result1b = asyncio.create_task(example1.data)

        assert await result1a == await result1b

        result2a = asyncio.create_task(example2.data)
        result2b = asyncio.create_task(example2.data)

        assert await result2a == await result2b

        assert await result1a != await result2a

    started_at = time.time()
    asyncio.run(main())
    assert time.time() - started_at < 0.03


if __name__ == "__main__":
    test()
