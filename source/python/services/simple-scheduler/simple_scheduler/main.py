import asyncio
import time

from functools import partial

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from simple_scheduler.deps.deps import Deps
from simple_scheduler.log_execution import log_execution
from telethon import TelegramClient
from telethon_playground.archive_all_chats import archive_all_chats


def main(env="test"):
    async def _main():
        # - Init deps

        deps = Deps.load(env=env)

        # - Start scheduler

        scheduler = AsyncIOScheduler()

        # - Clean messages every 15 minutes

        scheduler.add_job(func=partial(log_execution(archive_all_chats), await deps.started_telegram_user_client()))
        scheduler.add_job(
            func=partial(log_execution(archive_all_chats), await deps.started_telegram_user_client()),
            trigger=CronTrigger(minute="*/15"),
        )

        try:
            scheduler.start()

            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Scheduler stopped.")
        finally:
            await scheduler.shutdown()

    asyncio.run(_main())


if __name__ == "__main__":
    import fire

    fire.Fire(main)
