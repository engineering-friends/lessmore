import asyncio

from discord_to_telegram_forwarder.send_discord_post_to_telegram.send_discord_post_to_telegram import (
    send_discord_post_to_telegram,
)
from discord_to_telegram_forwarder.telegram_client import telegram_client


inputs_by_name = {
    "basic": dict(
        channel_name="channel_name",
        parent_channel_name="parent_channel_name",
        title="Basic",
        body="This is my body!",
        author_name="Mark Lidenberg",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
        emoji="💬",
    ),
    "no_body": dict(
        channel_name="channel_name",
        parent_channel_name="parent_channel_name",
        title="No body",
        body="",
        author_name="Mark Lidenberg",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
        emoji="📺",
    ),
    "with_emoji_in_title": dict(
        channel_name="channel_name",
        parent_channel_name="parent_channel_name",
        title="👾With emoji in title",
        body="",
        author_name="Mark Lidenberg",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
    ),
    "with_emoji_from_openai": dict(
        channel_name="channel_name",
        parent_channel_name="parent_channel_name",
        title="With emoji from openai",
        body="",
        author_name="Mark Lidenberg",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
    ),
    "with_inner_shortened_url": dict(
        channel_name="channel_name",
        parent_channel_name="parent_channel_name",
        title="With inner shortened url",
        body="",
        author_name="Mark Lidenberg",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=True,
        emoji="📺",
    ),
    "with_image": dict(
        author_name="Mark Lidenberg",
        title="Post with image",
        body="",
        channel_name="channel_name",
        parent_channel_name="parent_channel_name",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
        emoji="👍",
        files=["https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"],
    ),
}


async def test_batch():
    # - Init test

    from discord_to_telegram_forwarder.config.config import config

    await telegram_client.start(bot_token=config.telegram_bot_token)

    # - Send test_messages

    for input_ in inputs_by_name.values():
        await send_discord_post_to_telegram(
            telegram_chat_to_channel_name_rule={
                config.telegram_ef_discussions: lambda channel_name, parent_channel_name, category_name: True
            },
            **input_
        )


if __name__ == "__main__":
    asyncio.run(test_batch())
