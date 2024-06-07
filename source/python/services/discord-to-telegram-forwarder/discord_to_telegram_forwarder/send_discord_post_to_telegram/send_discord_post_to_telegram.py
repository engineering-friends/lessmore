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
from discord_to_telegram_forwarder.send_discord_post_to_telegram.ai.generate_image import generate_image
from discord_to_telegram_forwarder.send_discord_post_to_telegram.download_as_temp_file import _download_as_temp_file
from discord_to_telegram_forwarder.send_discord_post_to_telegram.format_message import format_message
from discord_to_telegram_forwarder.send_discord_post_to_telegram.get_shortened_url_from_tiny_url import (
    get_shortened_url_from_tiny_url,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.get_whois_url.get_whois_url import get_whois_url
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
from discord_to_telegram_forwarder.send_discord_post_to_telegram.utils.cache_on_disk import cache_on_disk
from loguru import logger
from PIL import Image
from pymaybe import maybe
from retry import retry
from telethon import functions, types

from lessmore.utils.file_primitives.write_file import write_file


MENTION_CHAR_PLACEHOLDER = "ç"

CAPTION_MESSAGE_LIMIT = 1024
MESSAGE_LIMIT = 4096


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
            if attachment.filename.lower().endswith((".webp", ".bmp")):
                # common image formats, not supported by telegram
                temp_path = _download_as_temp_file(attachment.url, extension=os.path.splitext(attachment.filename)[1])
                png_temp_path = to_png(temp_path)
                files.append(png_temp_path)
            else:
                # - Need to download videos

                temp_path = _download_as_temp_file(attachment.url, extension=os.path.splitext(attachment.filename)[1])
                files.append(temp_path)

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
    tags = [tag.name for tag in maybe(message).channel.applied_tags.or_else([])]
    body = message.content
    author_name = message.author.display_name
    url = message.jump_url

    # - Get author whois url

    try:
        author_whois_url = get_whois_url(name=author_name, deps=deps)
    except:
        logger.error("Failed to get author whois url", author_name=author_name)
        author_whois_url = ""

    # - Generate images if there are none

    if not files:
        # - Generate article cover

        try:
            image_contents = cache_on_disk(f"{deps.local_files_dir}/generate_image")(
                retry(tries=5, delay=1)(generate_image)
            )(
                prompt="\n".join([title, body]),
                pre_prompt="""
                        - There is an animated movie with a scene, that is described below. Describe the first shot of the scene
                        - EXCLUDE all electronic devices with screens (e.g. phones, laptops, etc.)
                        - It should be ONE shot, describing ONE scene. Choose any scene from the text
                        - It MUST have describe the text briefly, including it's core idea
                        - Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)
                        - Make it 15 words max
    
                        Examples of other scenes:
                        - A man is standing in the middle of the desert, looking at the sky, happy
                        - The night sky full of fireworks
                        - Winter landscape with houses, trees and snow covered mountain background, a sky filled with snowflakes
                        - A man finishing a grueling marathon race, crowd cheering, with a mountainous backdrop
                        - Man hands over documents at military registration desk, civilian officer reviews them, austere office setting
                        - Father and son discussing universities at home, papers with "PROS/CONS" lists on the table
                        - A man examining floating, digitally scanned leaves and branches in a virtual reality museum
    
                        The text: {prompt}""",
                style="Continuous lines very easy, very thin outline, clean and minimalist, black outline only, {prompt}",
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
            files = [filename]
        except Exception as e:
            logger.error("Failed to generate image", e=e)
            files = []

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

    # --- Crop body if necessary

    if body:
        # - First get full message text

        message_text_full = format_message(
            parent_channel_name=parent_channel_name,
            emoji=emoji,
            title=title,
            tags=tags,
            author_name=author_name,
            body=body,
            url=url,
            inner_shortened_url=inner_shortened_url,
            author_url=author_whois_url,
        )

        # - Then cut it to size limit

        body_size = len(body)
        non_body_size = len(message_text_full) - body_size
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
        inner_shortened_url=inner_shortened_url,
        author_url=author_whois_url,
    )

    # - Split files to separate message if needed

    message_text_and_files = []
    if files and (len(body) > CAPTION_MESSAGE_LIMIT - 50):
        # images have different limits, so we need to split them
        message_text_and_files.append(("", files))
        message_text_and_files.append((message_text, []))
    else:
        message_text_and_files.append((message_text, files))

    # - Send message to telegram

    for telegram_chat, filter_ in telegram_chat_to_filter.items():
        if filter_(message=message):
            # - Undownloaded videos and gifs can ONLY be sent as single files

            for _message_text, _files in message_text_and_files:
                # - Send message

                message = await deps.telegram_bot_client.send_message(
                    entity=telegram_chat,
                    file=(
                        _files[0] if len(_files) == 1 else _files or None
                    ),  # todo later: if >1 files - pick out gifs and send separately [@marklidenberg]
                    message=_message_text,
                    parse_mode="md",
                    link_preview=False,
                )

                # - Send reactions

                emojis = request_reaction_emojis_from_openai(f"{title} {body}")

                logger.debug("Emojis from openai", emojis=emojis)

                try:
                    await deps.telegram_user_client(
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

    deps = init_deps(env="prod")

    # - Start telegram bots

    await deps.telegram_bot_client.start(bot_token=deps.config.telegram_bot_token)
    await deps.telegram_user_client.start()

    # - Get discord client

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
            async for message in thread.history(limit=200):
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
                    filter_forum_post_messages=False,
                )
            except Exception as e:
                import traceback

                traceback.print_exc()

    # - Start discord client

    client = CustomDiscordClient(intents=discord.Intents.all())
    async with client:
        await client.start(token=deps.config.discord_token)


async def test():
    # - Init deps

    deps = init_deps()

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
                    # 'applied_tags': [Box({'name': 'tag1'}), Box({'name': 'tag2'})],
                },
                "content": """Я устроился на новую работу!""",
                "author": {"display_name": "Mark Lidenberg"},
                "jump_url": "https://discord.com/channels/1106702799938519211/1106702799938519213/913095424225706005",
                "attachments": [],
            }
        ),
        add_inner_shortened_url=True,
        telegram_chat_to_filter={deps.config.telegram_ef_channel: lambda message: True},
        filter_forum_post_messages=False,
    )


if __name__ == "__main__":
    asyncio.run(
        test_send_real_message_from_discord(
            forum_name="🗒│posts",
            title_contains="Про 3D Printing",
        )
    )

    # asyncio.run(test())
