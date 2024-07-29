import asyncio
import json
import time

from lessmore.utils.file_primitives.read_file import read_file
from lessmore.utils.file_primitives.write_file import write_file
from lessmore.utils.to_anything.to_datetime import to_datetime


class AsyncRateLimiter:
    """Rate limiter for async functions. Useful for limiting the rate of requests to an API."""

    def __init__(
        self,
        rate: int,
        period: int = 1,
        cache_path: str = "",
    ):
        self.rate = rate
        self.period_seconds = period
        self.cache_path = cache_path
        self.counter = 0
        self.lock = asyncio.Lock()
        self.last_reset = time.time()
        self.state_loaded = False

    async def acquire(self):
        # - Load state if needed

        if not self.state_loaded and self.cache_path:
            self.counter, self.last_reset = read_file(
                self.cache_path,
                default=(0, 0),
                reader=json.load,
            )
            self.state_loaded = True

        # - Acquire lock and check rate limit

        while True:
            async with self.lock:
                current_time = time.time()
                if current_time - self.last_reset >= self.period_seconds:
                    self.counter = 0
                    self.last_reset = current_time

                if self.counter < self.rate:
                    self.counter += 1

                    if self.cache_path:
                        write_file(
                            data=[self.counter, self.last_reset],
                            filename=self.cache_path,
                            writer=json.dump,
                        )

                    return
            await asyncio.sleep(0.01)  # Short sleep to prevent tight loop


def test():
    async def task(limiter, task_id):
        await limiter.acquire()
        print(f"Task {task_id}: Request allowed at {time.time()}")
        await asyncio.sleep(0.01)  # Simulate work

    async def main():
        limiter = AsyncRateLimiter(rate=2)
        tasks = [task(limiter, i) for i in range(10)]
        await asyncio.gather(*tasks)

    asyncio.run(main())


if __name__ == "__main__":
    test()
