import asyncio
import random

from discord_to_telegram_forwarder.config.config import config
from discord_to_telegram_forwarder.send_telegram_post.get_emoji_from_text import get_emoji_from_text
from discord_to_telegram_forwarder.telegram_client import telegram_client

from lessmore.utils.file_helpers.read_file import read_file
from lessmore.utils.path_helpers.get_current_dir import get_current_dir


async def send_telegram_post(channel_name: str, title: str, body: str, url: str):
    # - Read emoticons

    emoticons = read_file(str(get_current_dir() / "emoticons.txt")).strip().split("\n")

    # - Get emoji from openai

    emoji = get_emoji_from_text(f"{channel_name} {title} {body}")

    # - Format message for telegram

    text = ""
    if channel_name:
        text += f"#{channel_name.replace('-', '_')}\n"

    text += f"{emoji} **{title}**\n\n"
    text += (
        body[:3000] + ("" if len(body) < 3000 else "...") + "\n\n"
    )  # maximum telegram message size is 4096. Making it 3000 to resever space for title and for the buffer

    text += f"[→ к посту {random.choice(emoticons)}]({url})"

    # - Send message to telegram

    await telegram_client.send_message(
        entity="marklidenberg",
        message=text,
        parse_mode="md",
        link_preview=False,
    )


async def test():
    await telegram_client.start(bot_token=config.telegram_bot_token)
    await send_telegram_post(
        channel_name="channel_name",
        title="title",
        body="body",
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
    )


if __name__ == "__main__":
    asyncio.run(test())
