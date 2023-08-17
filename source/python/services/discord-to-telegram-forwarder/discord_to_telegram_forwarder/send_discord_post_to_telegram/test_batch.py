import asyncio

from discord_to_telegram_forwarder.send_discord_post_to_telegram.send_discord_post_to_telegram import (
    send_discord_post_to_telegram,
)
from discord_to_telegram_forwarder.telegram_client import telegram_client


inputs_by_name = {
    "basic": dict(
        channel_name="channel_name",
        title="Basic",
        body="This is my body!",
        author_name="Mark Lidenberg",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
        emoji="💬",
    ),
    "no_body": dict(
        channel_name="channel_name",
        title="No body",
        body="",
        author_name="Mark Lidenberg",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
        emoji="📺",
    ),
}


async def test_batch():
    # - Init test

    from discord_to_telegram_forwarder.config.config import config

    await telegram_client.start(bot_token=config.telegram_bot_token)

    # - Send test_messages

    for input_ in inputs_by_name.values():
        await send_discord_post_to_telegram(telegram_chat=config.telegram_chat, files=[], **input_)

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
    asyncio.run(test_batch())
