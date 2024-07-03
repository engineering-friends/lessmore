import asyncio
import inspect

from typing import Any, Awaitable


async def gather_nested(
    value: dict | list | Awaitable | Any,
    recursive: bool = True,
):
    if isinstance(value, dict):
        return {k: await gather_nested(v, recursive=recursive) for k, v in value.items()}
    elif isinstance(value, list):
        return [await gather_nested(v, recursive=recursive) for v in value]
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
        print(await gather_nested(value={i: test_func() for i in range(1000)}))

    asyncio.run(main())


if __name__ == "__main__":
    test()
