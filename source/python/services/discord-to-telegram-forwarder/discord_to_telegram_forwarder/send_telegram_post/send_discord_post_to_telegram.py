import asyncio
import random

from typing import Union

from discord_to_telegram_forwarder.config.config import config
from discord_to_telegram_forwarder.send_telegram_post.get_shortened_url import get_shortened_url
from discord_to_telegram_forwarder.send_telegram_post.request_emoji_from_openai import request_emoji_from_openai
from discord_to_telegram_forwarder.telegram_client import telegram_client

from lessmore.utils.file_helpers.read_file import read_file
from lessmore.utils.path_helpers.get_current_dir import get_current_dir


async def send_discord_post_to_telegram(
    telegram_chat: Union[str, int],
    post_forum_channel_name: str,
    post_title: str,
    post_body: str,
    post_url: str,
    add_inner_shortened_url: bool = True,
) -> None:
    # - Read emoticons

    emoticons = read_file(str(get_current_dir() / "emoticons.txt")).strip().split("\n")

    # - Get emoji from openai

    emoji = request_emoji_from_openai(f"{post_forum_channel_name} {post_title} {post_body}")

    # - Add discord:// to url and shorten it to make it https:// with redirection to discord://

    inner_shortened_url = get_shortened_url(f"discord://{post_url}") if add_inner_shortened_url else ""

    # - Format message for telegram

    text = ""
    if post_forum_channel_name:
        text += f"#{post_forum_channel_name.replace('-', '_')}\n"

    text += f"{emoji} **{post_title}**\n\n"
    text += (
        post_body[:3000] + ("" if len(post_body) < 3000 else "...") + "\n\n"
    )  # maximum telegram message size is 4096. Making it 3000 to resever space for title and for the buffer

    text += random.choice(emoticons) + "\n"
    text += f"[→ к посту]({post_url})"

    if inner_shortened_url:
        text += f"\n[→ к посту на apple-устройствах]({inner_shortened_url})"

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
        telegram_chat=-1001561135632,
        post_title="Тестирую форвардер",
        post_body="Здесь что-то оооочень важное",
        post_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=True,
    )


if __name__ == "__main__":
    asyncio.run(test())
