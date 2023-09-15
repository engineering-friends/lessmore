import asyncio

from box import Box

from discord_to_telegram_forwarder.send_discord_post_to_telegram.send_discord_post_to_telegram import (
    send_discord_post_to_telegram,
)
from discord_to_telegram_forwarder.telegram_client import telegram_client


inputs_by_name = {
    "basic": dict(
        message=Box(
            {
                "channel": {
                    "name": "basic",
                    "parent": {"name": "parent_channel_name"},
                },
                "content": "This is my body!",
                "author": {"display_name": "Mark Lidenberg"},
                "jump_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
                "attachments": [],
            }
        ),
        add_inner_shortened_url=False,
        emoji="💬",
    ),
    "no_body": dict(
        message=Box(
            {
                "channel": {
                    "name": "no_body",
                    "parent": {"name": "parent_channel_name"},
                },
                "content": "",
                "author": {"display_name": "Mark Lidenberg"},
                "jump_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
                "attachments": [],
            }
        ),
        add_inner_shortened_url=False,
        emoji="📺",
    ),
    "with_emoji_in_title": dict(
        message=Box(
            {
                "channel": {
                    "name": "👾with_emoji_in_title",
                    "parent": {"name": "parent_channel_name"},
                },
                "content": "",
                "author": {"display_name": "Mark Lidenberg"},
                "jump_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
                "attachments": [],
            }
        ),
        add_inner_shortened_url=False,
    ),
    "with_emoji_from_openai": dict(
        message=Box(
            {
                "channel": {
                    "name": "with_emoji_from_openai",
                    "parent": {"name": "parent_channel_name"},
                },
                "content": "",
                "author": {"display_name": "Mark Lidenberg"},
                "jump_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
                "attachments": [],
            }
        ),
        add_inner_shortened_url=False,
    ),
    "with_inner_shortened_url": dict(
        message=Box(
            {
                "channel": {
                    "name": "with_inner_shortened_url",
                    "parent": {"name": "parent_channel_name"},
                },
                "content": "",
                "author": {"display_name": "Mark Lidenberg"},
                "jump_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
                "attachments": [],
            }
        ),
        add_inner_shortened_url=True,
        emoji="📺",
    ),
    "with_image": dict(
        message=Box(
            {
                "channel": {
                    "name": "with_image",
                    "parent": {"name": "parent_channel_name"},
                },
                "content": "",
                "author": {"display_name": "Mark Lidenberg"},
                "jump_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
                "attachments": [{"url": "https://i.imgur.com/4M34hi2.png", 'filename': 'image.png'}],
            }
        ),
        add_inner_shortened_url=False,
        emoji="👍",
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
                config.telegram_ef_discussions: lambda message: True
            },
            **input_
        )


if __name__ == "__main__":
    asyncio.run(test_batch())
