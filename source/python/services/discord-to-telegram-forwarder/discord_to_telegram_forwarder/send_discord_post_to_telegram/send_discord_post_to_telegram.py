import asyncio
import re

from typing import Callable, Optional, Sequence, Union

import emoji as emoji_lib

from discord_to_telegram_forwarder.send_discord_post_to_telegram.get_shortened_url_from_tiny_url import (
    get_shortened_url_from_tiny_url,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.request_emoji_representing_text_from_openai import (
    request_emoji_representing_text_from_openai,
)
from discord_to_telegram_forwarder.telegram_client import telegram_client
from telethon import hints


TEMPLATE = """#{parent_channel_name}
{emoji} **{title}** by {author}
{body}
[→ к посту]({url}){apple_link}"""


async def send_discord_post_to_telegram(
    telegram_chat_to_channel_name_rule: dict[
        Union[str, int], Callable[[str, str, str], bool]
    ],  # def rule(chnanel_name:str, parent_channel_name:str, category_name: str) -> bool
    author_name: str,
    body: str,
    channel_name: str,
    parent_channel_name: str,
    category_name: str,
    title: str,
    url: str,
    add_inner_shortened_url: bool = True,
    emoji: Optional[str] = None,
    files: Sequence[hints.FileLike] = (),  # from telethon
) -> None:
    # - Prepare message text

    # -- Get emoji

    if not emoji:
        if emoji_lib.is_emoji(title[0]):
            # get from title
            emoji = title[0]
            title = title[1:]

            # remove space after emoji
            title = re.sub(r"^\s+", "", title)

        else:
            # get from openai
            emoji = request_emoji_representing_text_from_openai(f"{channel_name} {title} {body}")

    # -- Make discord schema and shorten it to make it https:// with redirection to discord://

    inner_shortened_url = (
        get_shortened_url_from_tiny_url(url.replace("https", "discord")) if add_inner_shortened_url else ""
    )

    # -- Replace @ for ~ in the body and title

    title = title.replace("@", "~")
    body = body.replace("@", "~")

    # -- Remove prefix emojis from parent channel name if any non-emoji characters are present

    if any([not emoji_lib.is_emoji(character) for character in parent_channel_name]):
        first_non_emoji_index = next(
            (index for index, character in enumerate(parent_channel_name) if not emoji_lib.is_emoji(character)), None
        )
        if first_non_emoji_index:
            parent_channel_name = parent_channel_name[first_non_emoji_index:]

    # -- Format message for telegram

    message_text = TEMPLATE.format(
        parent_channel_name=parent_channel_name.replace("-", "_"),
        emoji=emoji,
        title=title,
        author=author_name,
        body=("\n" + body[:3000] + ("" if len(body) < 3000 else "...")) + "\n" if body else "",
        url=url,
        apple_link=f" / [→ к посту для ]({inner_shortened_url})" if inner_shortened_url else "",
    )

    # - Send message to telegram

    for telegram_chat, channel_name_rule in telegram_chat_to_channel_name_rule.items():
        if channel_name_rule(
            channel_name=channel_name, parent_channel_name=parent_channel_name, category_name=category_name
        ):
            await telegram_client.send_message(
                entity=telegram_chat,
                message=message_text,
                parse_mode="md",
                link_preview=False,
                file=files or None,
            )


async def test():
    from discord_to_telegram_forwarder.config.config import config

    await telegram_client.start(bot_token=config.telegram_bot_token)
    await send_discord_post_to_telegram(
        author_name="Mark Lidenberg",
        title="⚙️Новая инженерная сессия!",
        body="Body",
        channel_name="channel_name",
        parent_channel_name="parent_channel_name",
        category_name="category_name",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=True,
        telegram_chat_to_channel_name_rule={
            config.telegram_ef_discussions: lambda channel_name, parent_channel_name, category_name: True
        },
        files=["https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"],
    )


if __name__ == "__main__":
    asyncio.run(test())
