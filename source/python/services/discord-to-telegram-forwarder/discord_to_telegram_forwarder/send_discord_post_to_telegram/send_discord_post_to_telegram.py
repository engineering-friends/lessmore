import asyncio
import io
import json
import os
import random
import re
import uuid

from typing import Callable, Optional, Union

import discord
import emoji as emoji_lib

from box import Box
from discord_to_telegram_forwarder.deps import Deps
from discord_to_telegram_forwarder.send_discord_post_to_telegram.ai.generate_article_cover import generate_article_cover
from discord_to_telegram_forwarder.send_discord_post_to_telegram.download_as_temp_file import _download_as_temp_file
from discord_to_telegram_forwarder.send_discord_post_to_telegram.format_message import format_message
from discord_to_telegram_forwarder.send_discord_post_to_telegram.get_notion_user_properties import (
    get_notion_user_properties,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.is_discord_channel_private import (
    is_discord_channel_private,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.request_emoji_representing_text_from_openai import (
    request_emoji_representing_text_from_openai,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.request_reaction_emoijs_from_openai import (
    request_reaction_emojis_from_openai,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.to_png import to_png
from lessmore.utils.cache_on_disk import cache_on_disk
from lessmore.utils.file_primitives.write_file import write_file
from loguru import logger
from PIL import Image
from pymaybe import maybe
from retry import retry
from telethon import TelegramClient, functions, types


MENTION_PLACEHOLDER = "ç"

CAPTION_MESSAGE_LIMIT = 1024
MESSAGE_LIMIT = 4096


async def send_discord_post_to_telegram(
    deps: Deps,
    message: discord.Message,
    telegram_user_client: TelegramClient,
    telegram_chat_to_filter: dict[
        Union[str, int], Callable[[discord.Message], bool]
    ],  # Telegram chat to filter function (if filter function returns True, message will be sent to this chat)
    filter_public_channels: bool = True,  # only send messages that are from public channels
    filter_forum_post_messages: bool = True,  # only send messages that are from forum channel and are starter message
    emoji: Optional[str] = None,  # if not provided, will be requested from openai
    telegram_username_to_discord_aliases_json: str = "{}",
) -> None:
    """Sends a discord message to telegram.

    Features:
    - Creates a cover image if no images are attached
    - Replaces discord placeholders in the message text with telegram-compatible placeholders (like fixing usernames)
    - Sends reactions to the message
    - Adds `notion_author_url` to the message text
    """

    # - Do not send in certain cases

    # -- Do not send if not a post message and `filter_forum_post_messages` is True

    if filter_forum_post_messages:
        is_post_message = isinstance(
            maybe(message).channel.parent.or_else(None), discord.ForumChannel
        ) and message.id == maybe(message).channel.starter_message.id.or_else(None)

        if not is_post_message:
            logger.info("Message is not a forum post message, skipping", message_id=message.id)
            return

    # -- Do not send if message is in a private channel and `filter_public_channels` is True

    if filter_public_channels:
        for channel_candidate in [
            message.channel,
            getattr(message.channel, "parent", None),
        ]:  # for forum messages, message.channel is a Thread, but message.channel.parent is a ForumChannel
            if isinstance(channel_candidate, discord.abc.GuildChannel):
                is_channel_private = is_discord_channel_private(channel_candidate)

                if is_channel_private:
                    logger.info("Channel is private, skipping", channel_id=channel_candidate.id)
                    return

    # - Download attachments locally, build `filenames` list

    filenames = []
    for attachment in message.attachments:
        if maybe(attachment).url.or_else(None) and maybe(attachment).filename.or_else(None):
            if attachment.filename.lower().endswith((".webp", ".bmp")):
                # common image formats, not supported by telegram
                temp_path = _download_as_temp_file(attachment.url, extension=os.path.splitext(attachment.filename)[1])
                png_temp_path = to_png(temp_path)
                filenames.append(png_temp_path)
            else:
                temp_path = _download_as_temp_file(attachment.url, extension=os.path.splitext(attachment.filename)[1])
                filenames.append(temp_path)

    # - Unfold message to variables

    channel_or_post_name = maybe(message).channel.name.or_else("")  # `Челленджи в EF`
    parent_channel_name = maybe(message).channel.parent.name.or_else("")  # `?│requests`
    title = maybe(message).channel.name.or_else("")  # `Челленджи в EF`
    tags = [tag.name for tag in maybe(message).channel.applied_tags.or_else([])]  # `['want_a_session']`
    body = message.content  # `Мы с другом раз в полгода...`
    author_name = message.author.display_name  # `Mark Lidenberg`
    url = message.jump_url  # `https://discord.com/...`

    # - Fix discord placeholders in the `body`: <@913095424225706005>, <#1106702799938519211>, <@&1106702799938519211> -> @marklidenberg, [name](link), @<name>

    # -- <@913095424225706005> -> <PLACEHOLDER>marklidenberg

    for user_id in re.findall(r"<@(\d+)>", message.content):  # <@913095424225706005>
        # - Get user

        user = message.guild.get_member(int(user_id))

        # - Load `telegram_username_to_discord_aliases`

        telegram_username_to_discord_aliases = json.loads(telegram_username_to_discord_aliases_json)

        discord_alias_to_telegram_username = {}
        for telegram_username, discord_aliases in telegram_username_to_discord_aliases.items():
            for discord_alias in discord_aliases:
                discord_alias_to_telegram_username[discord_alias] = telegram_username

        # - Get telegram username

        telegram_username = (
            discord_alias_to_telegram_username.get(user.nick)
            or discord_alias_to_telegram_username.get(user.global_name)
            or discord_alias_to_telegram_username.get(user.name)
        )

        # - Replace <@913095424225706005> with <@telegram_username> or <name>

        body = body.replace(
            f"<@{user_id}>",
            f"{MENTION_PLACEHOLDER}{telegram_username}" if telegram_username else user.display_name,
        )

    # -- <#1106702799938519211> -> [name](link)

    for channel_id in re.findall(r"<#(\d+)>", body):  # <#1106702799938519211>
        # - Get channel

        channel = message.guild.get_channel(int(channel_id))

        # - Replace <#1106702799938519211> with  [name](link)

        body = body.replace(f"<#{channel_id}>", f"[{channel.name}]({channel.jump_url})")

    # -- <@&1106702799938519211> -> @role_name

    for role_id in re.findall(r"<@&(\d+)>", body):  # <@&1106702799938519211>
        body = body.replace(f"<@&{role_id}>", message.guild.get_role(int(role_id)).name)

    # - Get user notion properties, extract `notion_ai_style` and `notion_author_url`

    try:
        notion_properties = await get_notion_user_properties(
            name=author_name,
            deps=deps,
        )  # {'AI стиль постов': 'style of secret of kells, old paper, celtic art', 'Name': 'Mark Lidenberg', 'TG_username': 'marklidenberg', 'url': 'https://www.notion.so/Mark-Lidenberg-d5ae5f192b4c402ba014268e63aed47c', 'Заполнена': True}
    except:
        logger.error("Failed to get user notion properties")

        notion_properties = {}

    notion_ai_style = notion_properties.get("AI стиль постов")
    notion_author_url = notion_properties.get("url", "")

    # - Generate an image cover if no images are attached, override `filenames` in this case

    if not filenames:
        try:
            # - Generate article cover

            image_contents = retry(tries=5, delay=1)(generate_article_cover)(
                title=title,
                body=body,
                style=notion_ai_style or "Continuous lines very easy, clean and minimalist, black and white",
            )

            # - Resize image to 1280x731 (telegram max size)

            image = Image.open(io.BytesIO(image_contents))
            image_resized = image.resize((1280, 731), Image.LANCZOS)
            image_contents = io.BytesIO()
            image_resized.save(image_contents, format="PNG")
            image_contents = image_contents.getvalue()

            # - Save to tmp file and add to files

            filename = f"/tmp/{uuid.uuid4()}.png"
            write_file(data=image_contents, filename=filename, as_bytes=True)
            filenames = [filename]
        except Exception as e:
            logger.error("Failed to generate image", e=e)

            filenames = []

    # - Prepare message text

    # -- Get emoji either from the title or from openai

    if not emoji:
        if emoji_lib.is_emoji(title[0]):
            # get from title
            emoji = title[0]
            title = title[1:]

            # remove space after emoji
            title = re.sub(r"^\s+", "", title)

        else:
            # get from openai
            emoji = request_emoji_representing_text_from_openai(f"{channel_or_post_name} {title} {body}")

    # -- Replace `@` for `~` in the body and title so that it doesn't try mention non-existing telegram users

    title = title.replace("@", "~")
    body = body.replace("@", "~")

    # -- Replace `MENTION_PLACEHOLDER` with `@`

    body = body.replace(MENTION_PLACEHOLDER, "@")

    # -- Remove prefix non-alphanumeric (or -) characters from `parent_channel_name` (name of the forum channel, where the post is located), so that it can be used as a tag

    def _is_alphanumeric_with_dashes(string: str) -> bool:
        return all([character.isalnum() or character == "-" for character in string])

    first_allowed_symbol_index = next(
        (index for index, character in enumerate(parent_channel_name) if _is_alphanumeric_with_dashes(character)),
        None,
    )
    if first_allowed_symbol_index:
        parent_channel_name = parent_channel_name[first_allowed_symbol_index:]

    # -- Format the message for telegram

    # --- Crop `body` if too long

    if body:
        body_size = len(body)
        non_body_size = (
            len(
                format_message(
                    parent_channel_name=parent_channel_name,
                    emoji=emoji,
                    title=title,
                    tags=tags,
                    author_name=author_name,
                    body=body,
                    url=url,
                    author_url=notion_author_url,
                )
            )
            - body_size
        )
        body_size_limit = MESSAGE_LIMIT - non_body_size - len("... (больше в посте)")
        body_size_limit -= (
            100  # for safety, as telegram could in theory have slightly different way of counting symbols
        )
        body = body[:body_size_limit] + ("" if len(body) < body_size_limit else "... (больше в посте)")

    # --- Format message text

    message_text = format_message(
        parent_channel_name=parent_channel_name,
        emoji=emoji,
        title=title,
        tags=tags,
        author_name=author_name,
        body=body,
        url=url,
        author_url=notion_author_url,
    )

    # - If the message is too long, split it into two messages: one with just image caption and another with the text

    message_text_and_files = []
    if filenames and (len(message_text) > CAPTION_MESSAGE_LIMIT):
        # images have different limits, so we need to split them
        message_text_and_files.append(("", filenames))
        message_text_and_files.append((message_text, []))
    else:
        message_text_and_files.append((message_text, filenames))

    # - Send the message to telegram

    for telegram_chat, filter_ in telegram_chat_to_filter.items():
        if filter_(message=message):
            for _message_text, _files in message_text_and_files:
                # - Send the message

                message = await telegram_user_client.send_message(
                    entity=telegram_chat,
                    file=(
                        _files[0] if len(_files) == 1 else _files or None
                    ),  # todo later: if >1 files - pick out gifs and send separately [@marklidenberg]
                    message=_message_text,
                    parse_mode="md",
                    link_preview=False,
                )

                # - Send reactions

                if random.uniform(0, 1) < 0.3:
                    emojis = request_reaction_emojis_from_openai(
                        f"{title} {body}",
                        limit=random.choice([1, 2, 3]),
                    )

                    logger.debug("Emojis from openai", emojis=emojis)

                    try:
                        await telegram_user_client(
                            functions.messages.SendReactionRequest(
                                peer=message.peer_id,
                                msg_id=message.id,
                                big=True,
                                add_to_recent=True,
                                reaction=[types.ReactionEmoji(emoticon=emoji) for emoji in reversed(emojis)],
                            )
                        )
                    except Exception as e:
                        logger.error("Failed to send reaction", e=e)


async def test_send_real_message_from_discord(forum_name: str, title_contains: str):
    # - Init deps

    deps = Deps.load(env="prod")

    # - Start telegram bots

    await deps.telegram_bot_client.start(bot_token=deps.config.telegram_bot_token)
    await deps.telegram_user_client.start()

    # - Custom discord client

    class CustomDiscordClient(discord.Client):
        async def on_ready(self):
            print("Logged on as", self.user)

            # - Get channel

            channels = sum([list(guild.channels) for guild in self.guilds], [])
            posts_channel = next((channel for channel in channels if channel.name == forum_name), None)
            if not posts_channel:
                print("No posts channel found")
                return

            thread = next((thread for thread in posts_channel.threads if title_contains in thread.name), None)

            if not thread:
                print("No thread found")
                return

            messages = []
            async for message in thread.history(limit=1):
                messages.append(message)

            if not messages:
                print("No messages found")
                return

            message = messages[0]

            # - Send message

            try:
                await send_discord_post_to_telegram(
                    deps=deps,
                    message=message,
                    telegram_chat_to_filter={deps.config.telegram_ef_channel: lambda message: True},
                    filter_public_channels=deps.config.filter_public_channels,
                    filter_forum_post_messages=False,
                )
            except Exception:
                import traceback

                traceback.print_exc()

    # - Start discord client

    client = CustomDiscordClient(intents=discord.Intents.all())
    async with client:
        await client.start(token=deps.config.discord_token)


async def test():
    # - Init deps

    deps = Deps.load()

    # - Start telegram bots

    await deps.telegram_bot_client.start(bot_token=deps.config.telegram_bot_token)
    await deps.telegram_user_client.start()

    # - Send message

    await send_discord_post_to_telegram(
        deps=deps,
        message=Box(  # note: test won't work with user_id, as it is not a discord.Message
            {
                "channel": {
                    "name": "Мета-исследование об эффекте кофе на организм",
                    "parent": {"name": "parent_channel_name"},
                    "applied_tags": [Box({"name": "tag1"}), Box({"name": "tag2"})],
                },
                "content": """Я устроился на новую работу!""",
                "author": {"display_name": "Mark Lidenberg"},
                "jump_url": "https://discord.com/channels/1106702799938519211/1106702799938519213/913095424225706005",
                "attachments": [],
            }
        ),
        filter_public_channels=True,
        telegram_chat_to_filter={deps.config.telegram_ef_channel: lambda message: True},
        filter_forum_post_messages=False,
        telegram_user_client=deps.telegram_user_client,
    )


if __name__ == "__main__":
    # asyncio.run(
    #     test_send_real_message_from_discord(
    #         forum_name="❔│requests",x
    #     )
    # )

    asyncio.run(test())
