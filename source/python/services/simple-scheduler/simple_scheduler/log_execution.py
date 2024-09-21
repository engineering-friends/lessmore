import asyncio
import time

from loguru import logger


def log_execution(func):
    async def wrapper(*args, **kwargs):
        # - Log

        logger.info(f"Started {func.__name__}(...)")

        # - Track execution time

        start_time = time.time()

        # - Run function

        result = await func(*args, **kwargs)

        # - Track execution time

        end_time = time.time()

        # - Log

        logger.info(f"Finished {func.__name__}(...)", elapsed=end_time - start_time)

        # - Return

        return result

    return wrapper


def test():
    async def main():
        await log_execution(func=asyncio.sleep)(1)

    asyncio.run(main())


if __name__ == "__main__":
    test()
