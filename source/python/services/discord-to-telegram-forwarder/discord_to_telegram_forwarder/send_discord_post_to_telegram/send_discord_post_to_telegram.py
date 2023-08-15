import asyncio

from typing import Sequence, Union

from discord_to_telegram_forwarder.send_discord_post_to_telegram.format_telegram_message_text import (
    format_telegram_message_text,
)
from discord_to_telegram_forwarder.telegram_client import telegram_client
from telethon import hints


async def send_discord_post_to_telegram(
    telegram_chat: Union[str, int],
    post_forum_channel_name: str,
    post_title: str,
    post_body: str,
    post_author_name: str,
    post_url: str,
    add_inner_shortened_url: bool = True,  # add discord:// url, shortened and wrapped into https://
    files: Sequence[hints.FileLike] = (),  # from telethon
) -> None:
    # - Send message to telegram

    await telegram_client.send_message(
        entity=telegram_chat,
        message=format_telegram_message_text(
            post_author_name=post_author_name,
            post_body=post_body,
            post_forum_channel_name=post_forum_channel_name,
            post_title=post_title,
            post_url=post_url,
            add_inner_shortened_url=add_inner_shortened_url,
        ),
        parse_mode="md",
        link_preview=False,
        file=files or None,
    )


async def test():
    from discord_to_telegram_forwarder.config.config import config

    await telegram_client.start(bot_token=config.telegram_bot_token)
    await send_discord_post_to_telegram(
        post_forum_channel_name="channel_name",
        telegram_chat=config.telegram_chat,
        post_title="Тестирую форвардер",
        post_body="",
        post_author_name="Mark Lidenberg",
        post_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=True,
        files=["https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"],
    )


if __name__ == "__main__":
    asyncio.run(test())
