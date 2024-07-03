import asyncio
import time


class AsyncRateLimiter:
    def __init__(self, rate: int, period: int = 1):
        self.rate = rate
        self.period = period
        self.counter = 0
        self.lock = asyncio.Lock()
        self.last_reset = time.time()

    async def acquire(self):
        while True:
            async with self.lock:
                current_time = time.time()
                if current_time - self.last_reset >= self.period:
                    self.counter = 0
                    self.last_reset = current_time

                if self.counter < self.rate:
                    self.counter += 1
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
