import asyncio

from typing import Sequence, Union

from discord_to_telegram_forwarder.send_discord_post_to_telegram.format_telegram_message_text.format_telegram_message_text import (
    format_telegram_message_text,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.test_post_kwargs import test_post_kwargs
from discord_to_telegram_forwarder.telegram_client import telegram_client
from telethon import hints


async def send_discord_post_to_telegram(
    telegram_chat: Union[str, int],
    files: Sequence[hints.FileLike] = (),  # from telethon
    **post_kwargs,
) -> None:
    # - Send message to telegram

    await telegram_client.send_message(
        entity=telegram_chat,
        message=format_telegram_message_text(**post_kwargs),
        parse_mode="md",
        link_preview=False,
        file=files or None,
    )


async def test_single():
    from discord_to_telegram_forwarder.config.config import config

    await telegram_client.start(bot_token=config.telegram_bot_token)

    await send_discord_post_to_telegram(
        author_name="Mark Lidenberg",
        title="Как обходить ограниченный контекст в ChatGPT для больших тасок?",
        body="Body",
        channel_name="channel_name",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
        emoji="👍",
        telegram_chat=config.telegram_chat,
        files=["https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"],
    )


async def test_batch():
    # - Init test
    from discord_to_telegram_forwarder.config.config import config

    await telegram_client.start(bot_token=config.telegram_bot_token)

    # - Send test_messages

    for post_kwargs in test_post_kwargs.values():
        await send_discord_post_to_telegram(telegram_chat=config.telegram_chat, files=[], **post_kwargs)

    # - Send with image

    await send_discord_post_to_telegram(
        author_name="Mark Lidenberg",
        title="Post with image",
        body="",
        channel_name="channel_name",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
        emoji="👍",
        telegram_chat=config.telegram_chat,
        files=["https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"],
    )

    # - Send dynamic emoji from openai and apple-link

    await send_discord_post_to_telegram(
        author_name="Mark Lidenberg",
        title="Post with dynamic emoji and apple-link",
        body="",
        channel_name="channel_name",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=True,
        telegram_chat=config.telegram_chat,
    )


if __name__ == "__main__":
    # asyncio.run(test_single())
    asyncio.run(test_batch())
