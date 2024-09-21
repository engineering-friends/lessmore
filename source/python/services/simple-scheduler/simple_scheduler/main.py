import asyncio
import time

from datetime import timedelta
from functools import partial

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from simple_scheduler.deps.deps import Deps
from simple_scheduler.log_execution import log_execution
from telethon import TelegramClient
from telethon_playground.archive_all_chats import archive_all_chats
from telethon_playground.filter_folder_unread import filter_folder_unread
from telethon_playground.mute_unmute_recent_chats import start_muting_unmuting_recent_chats


def main(env="test"):
    async def _main():
        # - Init deps

        deps = Deps.load(env=env)

        # - Get telegram client

        client = await deps.started_telegram_user_client()

        # - Mute-unmute recent chats

        await start_muting_unmuting_recent_chats(client=client, offset=timedelta(hours=4))

        # - Start scheduler

        scheduler = AsyncIOScheduler()

        # - Clean messages every 15 minutes

        scheduler.add_job(
            func=partial(log_execution(archive_all_chats), client=client),
            trigger=IntervalTrigger(minutes=15),
        )
        scheduler.add_job(
            func=partial(log_execution(filter_folder_unread), client=client, folder_name="Groups"),
            trigger=IntervalTrigger(minutes=15),
        )
        scheduler.add_job(
            func=partial(log_execution(filter_folder_unread), client=client, folder_name="Daily"),
            trigger=IntervalTrigger(minutes=15),
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
