import asyncio
import re

import discord

from box import Box
from discord_to_telegram_forwarder.deps.deps import Deps
from discord_to_telegram_forwarder.deps.init_deps import init_deps
from discord_to_telegram_forwarder.update_comments_counter.search_telegram_messages import search_telegram_messages
from loguru import logger
from pymaybe import maybe


async def update_comments_counter(
    deps: Deps,
    message: discord.Message,
    channels: list[str | int],
) -> None:
    # - Find telegram message

    telegram_messages = sum(
        [
            await search_telegram_messages(deps=deps, channel=channel, query=message.channel.name)
            for channel in channels
        ],
        [],
    )

    if not telegram_messages:
        logger.warning(f"Telegram message not found for discord message", content=message.content)
        return

    telegram_message = telegram_messages[0]

    # - Update text

    text = telegram_messages[0].text

    comments_count = 0 if maybe(message).channel.starter_message.id.or_else("") == message.id else message.position + 1

    # "(+2)" or "" -> "(+3)"
    if re.search(r"\(\+?\d+\)$", text):
        text = re.sub(r"\(\+?\d+\)$", f"({'+' if comments_count else ''}{comments_count})", text)
    else:
        text = text.rstrip()
        text = text + f" ({'+' if comments_count else ''}{comments_count})"

    logger.info(
        "Updating telegram message message",
        original_text=telegram_messages[0].text,
        text=text,
        discord_message_content=message.content,
        comments_count=comments_count,
        message_position=message.position,
        message_id=message.id,
        starter_message_id=maybe(message).channel.starter_message.id.or_else(""),
    )

    # - Edit message

    if telegram_messages[0].text == text:
        logger.info("Text is the same, skipping")
        return

    await deps.telegram_user_client.edit_message(
        entity=telegram_messages[0],
        message=text,
        parse_mode="md",
        link_preview=False,
        file=telegram_message.file,
    )


async def test():
    # - Init hub

    deps = init_deps()

    # - Start client

    await deps.telegram_user_client.start()
    await update_comments_counter(
        deps=deps,
        message=Box(
            {
                "channel": {
                    "name": "Foo by Mark Lidenberg",
                    "starter_message": {"id": 123},
                },
                "position": 123,
                "id": "id",
                "content": "content",
            }
        ),
        channels=[-1001897462358],  # EF: Test
    )


if __name__ == "__main__":
    asyncio.run(test())
