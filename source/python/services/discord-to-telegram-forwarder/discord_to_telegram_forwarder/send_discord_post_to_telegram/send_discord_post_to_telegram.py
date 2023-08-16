import asyncio

from typing import Sequence, Union

from discord_to_telegram_forwarder.send_discord_post_to_telegram.format_telegram_message_text import (
    format_telegram_message_text,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.tests.messages import test_messages
from discord_to_telegram_forwarder.telegram_client import telegram_client
from telethon import hints


async def send_discord_post_to_telegram(
    telegram_chat: Union[str, int],
    format_telegram_message_text_kwargs: dict,
    files: Sequence[hints.FileLike] = (),  # from telethon
) -> None:
    # - Send message to telegram

    await telegram_client.send_message(
        entity=telegram_chat,
        message=format_telegram_message_text(**format_telegram_message_text_kwargs),
        parse_mode="md",
        link_preview=False,
        file=files or None,
    )


async def test_single():
    from discord_to_telegram_forwarder.config.config import config

    await telegram_client.start(bot_token=config.telegram_bot_token)

    await send_discord_post_to_telegram(
        format_telegram_message_text_kwargs=dict(
            post_author_name="Mark Lidenberg",
            post_title="Как обходить ограниченный контекст в ChatGPT для больших тасок?",
            post_body="Body",
            post_forum_channel_name="channel_name",
            post_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
            add_inner_shortened_url=False,
            emoji="👍",
        ),
        telegram_chat=config.telegram_chat,
        files=["https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"],
    )


async def test_batch():
    from discord_to_telegram_forwarder.config.config import config

    await telegram_client.start(bot_token=config.telegram_bot_token)

    # - Send all

    for message in test_messages.values():
        await send_discord_post_to_telegram(
            telegram_chat=config.telegram_chat,
            format_telegram_message_text_kwargs=message,
            files=[],
        )

    # - Send with image

    await send_discord_post_to_telegram(
        format_telegram_message_text_kwargs=dict(
            post_author_name="Mark Lidenberg",
            post_title="Post with image",
            post_body="",
            post_forum_channel_name="channel_name",
            post_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
            add_inner_shortened_url=False,
            emoji="👍",
        ),
        telegram_chat=config.telegram_chat,
        files=["https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"],
    )

    # - Send emoji and apple-link

    await send_discord_post_to_telegram(
        format_telegram_message_text_kwargs=dict(
            post_author_name="Mark Lidenberg",
            post_title="Post with dynamic emoji and apple-link",
            post_body="",
            post_forum_channel_name="channel_name",
            post_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
            add_inner_shortened_url=True,
        ),
        telegram_chat=config.telegram_chat,
    )


if __name__ == "__main__":
    # asyncio.run(test_single())
    asyncio.run(test_batch())
