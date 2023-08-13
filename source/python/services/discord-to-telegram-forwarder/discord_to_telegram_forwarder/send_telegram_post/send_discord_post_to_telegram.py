import asyncio
import random

from discord_to_telegram_forwarder.config.config import config
from discord_to_telegram_forwarder.send_telegram_post.request_emoji_from_openai import request_emoji_from_openai
from discord_to_telegram_forwarder.telegram_client import telegram_client

from lessmore.utils.file_helpers.read_file import read_file
from lessmore.utils.path_helpers.get_current_dir import get_current_dir


async def send_discord_post_to_telegram(
    telegram_chat: str,
    post_forum_channel_name: str,
    post_title: str,
    post_body: str,
    post_url: str,
) -> None:
    # - Read emoticons

    emoticons = read_file(str(get_current_dir() / "emoticons.txt")).strip().split("\n")

    # - Get emoji from openai

    emoji = request_emoji_from_openai(f"{post_forum_channel_name} {post_title} {post_body}")

    # - Format message for telegram

    text = ""
    if post_forum_channel_name:
        text += f"#{post_forum_channel_name.replace('-', '_')}\n"

    text += f"{emoji} **{post_title}**\n\n"
    text += (
        post_body[:3000] + ("" if len(post_body) < 3000 else "...") + "\n\n"
    )  # maximum telegram message size is 4096. Making it 3000 to resever space for title and for the buffer

    text += f"[→ к посту {random.choice(emoticons)}]({post_url})"

    # - Send message to telegram

    await telegram_client.send_message(
        entity=telegram_chat,
        message=text,
        parse_mode="md",
        link_preview=False,
    )


async def test():
    await telegram_client.start(bot_token=config.telegram_bot_token)
    await send_discord_post_to_telegram(
        post_forum_channel_name="channel_name",
        telegram_chat="marklidenberg",
        post_title="title",
        post_body="body",
        post_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
    )


if __name__ == "__main__":
    asyncio.run(test())
