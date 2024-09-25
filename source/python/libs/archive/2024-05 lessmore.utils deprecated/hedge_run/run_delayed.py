import asyncio


async def run_delayed(func, delay, kwargs=None):
    kwargs = kwargs or {}
    await asyncio.sleep(delay)
    return await func(**kwargs)


def test():
    async def f():
        print("Start f")
        await asyncio.sleep(1)
        print("Finish f")
        return 1

    print("Start")
    print(asyncio.run(run_delayed(f, delay=1)))


if __name__ == "__main__":
    test()
