import asyncio

from typing import Callable, Optional

from lessmore.utils.hedge_run.run_delayed import run_delayed


async def hedge_run(
    func: Callable,
    delay: float,
    max_times: int,
    kwargs: Optional[dict] = None,
):
    """Run function multiple times concurrently with delay between runs until first concurrent call succeeds. Do not wait for other calls to finish."""

    # - Init tasks

    tasks = [asyncio.create_task(run_delayed(func, delay=i * delay, kwargs=kwargs)) for i in range(max_times)]

    # - Run tasks until first succeeds

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # - Cancel pending tasks

    for task in pending:
        task.cancel()

    # - Return result from the first completed task

    for task in done:
        return task.result()

    # - Assert notice

    assert False, "Should not happen, result should be returned on the step above"


def test():
    import asyncio
    import random

    async def f():

        # - Init sleeping period

        random_sleep_period = random.randint(1, 5)

        # - Print sleeping period

        print(f"Running f: {random_sleep_period}")

        # - Sleep

        await asyncio.sleep(random_sleep_period)

        # - Return

        return random_sleep_period

    print(asyncio.run(hedge_run(f, delay=1, max_times=5)))


if __name__ == "__main__":
    test()
