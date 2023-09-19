import asyncio
import re

import discord

from box import Box
from deeplay.utils.json_utils import to_json
from deeplay.utils.print_json import print_json
from discord_to_telegram_forwarder.telegram_clients.telegram_user_client import telegram_user_client
from loguru import logger


async def update_comments_counter(message: discord.Message, channels: list[str]) -> None:
    # - Find telegram message

    telegram_messages = sum(
        [
            [message async for message in telegram_user_client.iter_messages(channel, search=message.channel.name)]
            for channel in channels
        ],
        [],
    )

    if not telegram_messages:
        logger.warning(f"Telegram message not found for discord message", content=message.text)
        return
    telegram_message = telegram_messages[0]

    # - Update text

    text = telegram_messages[0].text

    comments_count = message.position + 1

    # "(+2)" or "" -> "(+3)"
    if re.search(r"\(\+?\d+\)$", text):
        text = re.sub(r"\(\+?\d+\)$", f"({'+' if comments_count else ''}{comments_count})", text)
    else:
        text = text.rstrip()
        text = text + f" ({'+' if comments_count else ''}{comments_count})"

    # - Edit message

    await telegram_user_client.edit_message(
        entity=telegram_messages[0],
        message=text,
        parse_mode="md",
        link_preview=False,
        file=telegram_message.file,
    )


async def test():
    await telegram_user_client.start()
    await update_comments_counter(
        message=Box({"channel": {"name": "New post by Mark Lidenberg"}, "position": 6}),
        channels=["-1001897462358"],  # EF: Test
    )


if __name__ == "__main__":
    asyncio.run(test())
