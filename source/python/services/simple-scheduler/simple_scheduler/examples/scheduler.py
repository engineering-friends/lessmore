import asyncio
import os

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger


async def foo():
    # Your function logic here
    print("Running foo()")

    # Configure loguru to write to a file with a timestamp
    log_file = f'logs/foo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logger.add(log_file, rotation="1 day")

    logger.info("Starting foo() execution")

    # Add your function logic here
    logger.info("This is a log message from foo()")

    # Simulate some asynchronous work
    await asyncio.sleep(1)

    logger.info("Finished foo() execution")

    # Remove the file handler after we're done
    logger.remove()


async def main():
    os.makedirs("logs", exist_ok=True)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(func=foo)  # immediate execution
    scheduler.add_job(func=foo, trigger=CronTrigger(minute="*/5"))  # every 5 minutes
    # scheduler.add_job(func=foo, trigger=IntervalTrigger(seconds=10))
    # scheduler.add_job(func=foo, trigger=DateTrigger())

    try:
        scheduler.start()
        print("Starting scheduler. Press Ctrl+C to exit.")

        # Keep the main coroutine running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped.")
    finally:
        await scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
