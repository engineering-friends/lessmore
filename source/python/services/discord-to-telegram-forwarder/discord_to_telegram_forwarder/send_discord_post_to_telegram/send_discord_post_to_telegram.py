import asyncio
import io
import json
import os
import re
import uuid

from typing import Callable, Optional, Union

import discord
import emoji as emoji_lib

from box import Box
from discord_to_telegram_forwarder.deps.deps import Deps
from discord_to_telegram_forwarder.deps.init_deps import init_deps
from discord_to_telegram_forwarder.send_discord_post_to_telegram.download_as_temp_file import _download_as_temp_file
from discord_to_telegram_forwarder.send_discord_post_to_telegram.format_message import format_message
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.cache_on_disk import (
    cache_on_disk,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.generate_image_old import (
    generate_image,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.get_shortened_url_from_tiny_url import (
    get_shortened_url_from_tiny_url,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.is_discord_channel_private import (
    is_discord_channel_private,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.request_emoji_representing_text_from_openai import (
    request_emoji_representing_text_from_openai,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.to_png import to_png
from loguru import logger
from PIL import Image
from pymaybe import maybe
from utils_ak.os import open_file_in_os

from lessmore.utils.file_utils.write_file import write_file


MENTION_CHAR_PLACEHOLDER = "ç"


async def send_discord_post_to_telegram(
    deps: Deps,
    message: discord.Message,
    telegram_chat_to_filter: dict[Union[str, int], Callable[[discord.Message], bool]],
    filter_forum_post_messages: bool = True,
    emoji: Optional[str] = None,
    add_inner_shortened_url: bool = True,
) -> None:
    # - Filter forum post messages: from forum channel and is starter message

    if filter_forum_post_messages:
        is_post_message = isinstance(
            maybe(message).channel.parent.or_else(None), discord.ForumChannel
        ) and message.id == maybe(message).channel.starter_message.id.or_else(None)

        if not is_post_message:
            logger.info("Message is not a forum post message, skipping", message_id=message.id)
            return

    # - Filter public

    if deps.config.filter_public_channels:
        for channel_candidate in [
            message.channel,
            getattr(message.channel, "parent", None),
        ]:  # for forum messages, message.channel is a Thread, but message.channel.parent is a ForumChannel
            if isinstance(channel_candidate, discord.abc.GuildChannel):
                is_channel_private = is_discord_channel_private(channel_candidate)

                if is_channel_private:
                    logger.info("Channel is private, skipping", channel_id=channel_candidate.id)
                    return

    # - Get image attachments

    files = []
    for attachment in message.attachments:
        if maybe(attachment).url.or_else(None) and maybe(attachment).filename.or_else(None):
            if attachment.filename.lower().endswith((".mp4", ".avi", ".mov")) and len(message.attachments) > 1:
                # - Need to download videos
                temp_path = _download_as_temp_file(attachment.url, attachment.filename)
                files.append(temp_path)
            elif attachment.filename.lower().endswith((".webp", ".bmp")):
                # common image formats, not supported by telegram
                temp_path = _download_as_temp_file(attachment.url, attachment.filename)
                png_temp_path = to_png(temp_path)
                files.append(png_temp_path)
            else:
                files.append(attachment.url)

    # - Get discord_alias_to_telegram_username

    telegram_username_to_discord_aliases = json.loads(deps.config.telegram_username_to_discord_aliases_json)

    discord_alias_to_telegram_username = {}
    for telegram_username, discord_aliases in telegram_username_to_discord_aliases.items():
        for discord_alias in discord_aliases:
            discord_alias_to_telegram_username[discord_alias] = telegram_username

    # - Fix usernames in message text and replace with telegram tags / discord display name

    for user_id in re.findall(r"<@(\d+)>", message.content):  # <@913095424225706005>
        # - Get user

        user = message.guild.get_member(int(user_id))

        # - Get telegram username

        telegram_username = (
            discord_alias_to_telegram_username.get(user.nick)
            or discord_alias_to_telegram_username.get(user.global_name)
            or discord_alias_to_telegram_username.get(user.name)
        )

        # - Replace <@913095424225706005> with <@telegram_username> or <name>

        message.content = message.content.replace(
            f"<@{user_id}>",
            f"{MENTION_CHAR_PLACEHOLDER}{telegram_username}" if telegram_username else user.display_name,
        )

    # - Find all channels and replace with links

    for channel_id in re.findall(r"<#(\d+)>", message.content):  # <#1106702799938519211>
        # - Get channel

        channel = message.guild.get_channel(int(channel_id))

        # - Replace <#1106702799938519211> with <name>

        message.content = message.content.replace(f"<#{channel_id}>", f"[{channel.name}]({channel.jump_url})")

    # - Find all roles and replace with their names

    for role_id in re.findall(r"<@&(\d+)>", message.content):  # <@&1106702799938519211>
        # - Get role

        role = message.guild.get_role(int(role_id))

        # - Replace <@&1106702799938519211> with @<name>

        message.content = message.content.replace(f"<@&{role_id}>", f"{role.name}")

    # - Unfold message

    channel_name = maybe(message).channel.name.or_else("")
    parent_channel_name = maybe(message).channel.parent.name.or_else("")
    title = maybe(message).channel.name.or_else("")
    body = message.content
    author_name = message.author.display_name
    url = message.jump_url

    # - Generate images if there are none

    if not files:
        # - Generate article cover

        image_contents = cache_on_disk()(generate_image)(
            text="\n".join([title, body]),
            text_prompt="",
            image_prompt="Anime:",
        ).image_contents

        # - Resize image to 1280x731 (telegram max size)

        image = Image.open(io.BytesIO(image_contents))
        image_resized = image.resize((1280, 731), Image.LANCZOS)
        image_contents = io.BytesIO()
        image_resized.save(image_contents, format="PNG")
        image_contents = image_contents.getvalue()

        # - Save to tmp file and add to files

        filename = f"/tmp/{uuid.uuid4()}.png"
        write_file(data=image_contents, path=filename, as_bytes=True)
        files = [filename]

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

    # -- Allow specific user mentions from dicsord to bypass the filter

    body = body.replace(MENTION_CHAR_PLACEHOLDER, "@")

    # -- Remove prefix non-alhpanumeric (or -) characters from parent_channel_name

    def _is_alphanumeric_with_dashes(string: str) -> bool:
        return all([character.isalnum() or character == "-" for character in string])

    first_allowed_symbol_index = next(
        (index for index, character in enumerate(parent_channel_name) if _is_alphanumeric_with_dashes(character)),
        None,
    )
    if first_allowed_symbol_index:
        parent_channel_name = parent_channel_name[first_allowed_symbol_index:]

    # -- Format message for telegram

    # --- Limit

    message_size_limit = 4096 if not files else 1024  # 4096 is telegram message size limit, but caption limit is 1024

    # --- Crop body if necessary

    if body:
        # - First get full message text

        message_text_full = format_message(
            parent_channel_name=parent_channel_name,
            emoji=emoji,
            title=title,
            author_name=author_name,
            body=body,
            url=url,
            inner_shortened_url=inner_shortened_url,
        )

        # - Then cut it to size limit

        body_size = len(body)
        non_body_size = len(message_text_full) - body_size
        body_size_limit = message_size_limit - non_body_size - 3  # 3 is for extra "..." added in the end
        body_size_limit -= (
            100  # for safety, as telegram could in theory have slightly different way of counting symbols
        )
        body = body[:body_size_limit] + ("" if len(body) < body_size_limit else "...")

    # --- Format message text

    message_text = format_message(
        parent_channel_name=parent_channel_name,
        emoji=emoji,
        title=title,
        author_name=author_name,
        body=body,
        url=url,
        inner_shortened_url=inner_shortened_url,
    )

    # - Send message to telegram

    for telegram_chat, filter_ in telegram_chat_to_filter.items():
        if filter_(message=message):
            # - Undownloaded videos and gifs can ONLY be sent as single files

            # todo later: if >1 files - pick out gifs and send separately [@marklidenberg]
            await deps.telegram_bot_client.send_message(
                entity=telegram_chat,
                file=files[0] if len(files) == 1 else files or None,
                message=message_text,
                parse_mode="md",
                link_preview=False,
            )


async def test():
    # - Init deps

    deps = init_deps()

    # - Start telegram bots

    await deps.telegram_bot_client.start(bot_token=deps.config.telegram_bot_token)

    # - Send message

    await send_discord_post_to_telegram(
        deps=deps,
        message=Box(  # note: test won't work with user_id, as it is not a discord.Message
            {
                "channel": {
                    "name": "Мета-исследование об эффекте кофе на организм",
                    "parent": {"name": "parent_channel_name"},
                },
                "content": """1) На скриншоте - исследование про генетическую чувствительность к разным эффектам кофе.
TL;DR строго индивидуально
2) Статья - https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8070495/
tl;dr Кофе снижает смертность от всех причин
Mark Lidenberg На счет того пить или не пить и что для кого правильно :)""",
                "author": {"display_name": "Mark Lidenberg"},
                "jump_url": "https://discord.com/channels/1106702799938519211/1106702799938519213/913095424225706005",
                "attachments": [],
            }
        ),
        add_inner_shortened_url=True,
        telegram_chat_to_filter={deps.config.telegram_ef_discussions: lambda message: True},
        filter_forum_post_messages=False,
    )


if __name__ == "__main__":
    asyncio.run(test())
