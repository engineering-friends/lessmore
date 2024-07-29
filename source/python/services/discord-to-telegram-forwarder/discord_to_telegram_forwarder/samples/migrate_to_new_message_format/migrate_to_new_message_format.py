import asyncio
import json

from pathlib import Path

import keyring

from discord_to_telegram_forwarder.deps import Deps
from discord_to_telegram_forwarder.samples.migrate_to_new_message_format.format_message import format_message
from lessmore.utils.asynchronous.async_rate_limiter import AsyncRateLimiter
from lessmore.utils.track import track
from telethon import TelegramClient


rate_limiters = (
    AsyncRateLimiter(
        rate=10,
        period=1,
        cache_path="/tmp/telegram_rate_limiter_1.json",
    ),
    AsyncRateLimiter(
        rate=15,
        period=60,
        cache_path="/tmp/telegram_rate_limiter_60.json",
    ),
)


async def migrate_to_new_message_format(channel: int = -1001897462358):  # ef test
    # - Init deps

    deps = Deps.load()

    # - Start telegram bots

    await deps.telegram_user_client.start()

    # - Get all messages

    messages = await deps.telegram_user_client.get_messages(channel, limit=None)

    # - Update messages

    for message in track(messages):
        if not message.text:
            continue

        new_text = format_message(message.text)
        if new_text != message.text:
            for rate_limiter in rate_limiters:
                await rate_limiter.acquire()

            await deps.telegram_user_client.edit_message(
                entity=channel,
                message=message,
                text=new_text,
                link_preview=False,
            )


if __name__ == "__main__":
    asyncio.run(migrate_to_new_message_format(channel=-1001722020175))
    # asyncio.run(migrate_to_new_message_format())
