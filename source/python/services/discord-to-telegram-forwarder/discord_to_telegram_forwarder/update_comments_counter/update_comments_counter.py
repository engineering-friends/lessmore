import asyncio
import re

import discord

from box import Box
from discord_to_telegram_forwarder.deps import Deps
from discord_to_telegram_forwarder.update_comments_counter.search_telegram_messages import search_telegram_messages
from loguru import logger
from more_itertools import first
from pymaybe import maybe


async def update_comments_counter(
    deps: Deps,
    message: discord.Message,
    channels: list[str | int],
) -> None:
    """Adds comment counter from Discord: `→ обсудить в дискорде` -> `→ обсудить в дискорде (0)`"""

    # - Find telegram message

    telegram_message = first(
        sum(
            [
                await search_telegram_messages(deps=deps, channel=channel, query=message.channel.name)
                for channel in channels
            ],
            [],
        ),
        default=None,
    )

    if not telegram_message:
        logger.warning("Telegram message not found for discord message", content=message.content)
        return

    # - Update text

    text = telegram_message.text

    comments_count = 0 if maybe(message).channel.starter_message.id.or_else("") == message.id else message.position + 1

    if comments_count == 0:
        logger.info("No comments, skipping")
        return

    # "(+2)" or "" -> "(+3)"
    text = re.sub(
        r"→ обсудить в дискорде(\s*\(\+?\d+\))*",
        f"→ обсудить в дискорде (+{comments_count})",
        text,
    )

    logger.info(
        "Updating telegram message message",
        original_text=telegram_message.text,
        text=text,
        discord_message_content=message.content,
        comments_count=comments_count,
        message_position=message.position,
        message_id=message.id,
        starter_message_id=maybe(message).channel.starter_message.id.or_else(""),
    )

    # - Edit message

    if telegram_message.text == text:
        logger.info("Text is the same, skipping")
        return

    await deps.telegram_user_client.edit_message(
        entity=telegram_message,
        message=text,
        parse_mode="md",
        link_preview=False,
        file=telegram_message.file,
    )


async def test():
    # - Init hub

    deps = Deps.load()

    # - Start client

    await deps.telegram_user_client.start()
    await update_comments_counter(
        deps=deps,
        message=Box(
            {
                "channel": {
                    "name": "Мета-исследование об эффекте кофе на организм",
                    "starter_message": {"id": -1},
                },
                "position": -1,
                "id": "id",
                "content": "content",
            }
        ),
        channels=[-1001897462358],  # EF: Test
    )


if __name__ == "__main__":
    asyncio.run(test())
