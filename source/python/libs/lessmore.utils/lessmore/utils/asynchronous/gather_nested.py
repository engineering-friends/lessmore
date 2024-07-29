import asyncio
import inspect
import time

from typing import Any, Awaitable


async def gather_nested(
    value: dict | list | Awaitable | Any,
    recursive: bool = True,
) -> dict | list | Any:
    """Run all awaitables in a nested structure concurrently."""
    if isinstance(value, dict):
        results = await asyncio.gather(*(gather_nested(v, recursive=recursive) for v in value.values()))
        return dict(zip(value.keys(), results))
    elif isinstance(value, list):
        return await asyncio.gather(*(gather_nested(v, recursive=recursive) for v in value))
    elif inspect.isawaitable(value):
        if recursive:
            return await gather_nested(await value, recursive=recursive)
        else:
            return await value
    else:
        return value


def test():
    async def test_func():
        await asyncio.sleep(0.01)
        return "Done!"

    async def main():
        started_at = time.time()
        await gather_nested(value={i: test_func() for i in range(100)})
        assert time.time() - started_at < 0.1

    asyncio.run(main())


if __name__ == "__main__":
    test()
