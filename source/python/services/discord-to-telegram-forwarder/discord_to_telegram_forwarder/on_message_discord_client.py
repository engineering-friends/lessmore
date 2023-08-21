import asyncio
import re

from typing import Callable

import discord

from discord_to_telegram_forwarder.config.config import config
from loguru import logger
from pymaybe import maybe

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru


# - Init discord client


class OnMessageDiscordClient(discord.Client):
    def __init__(
        self,
        *args,
        process_message: Callable,
        filter_forum_post_messages: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.process_message = process_message
        self.filter_forum_post_messages = filter_forum_post_messages

    async def on_ready(self):
        logger.info(f"Logged in", user=self.user, id=self.user.id)

    async def on_message(self, message: discord.Message):
        # - Log message

        logger.info(
            "Received message",
            value=dict(
                id=message.id,
                jump_url=message.jump_url,
                content=message.content,
                type=message.type,
                author_name=message.author.name,
                author_global_name=message.author.global_name,
                author_display_name=message.author.display_name,
                author_id=message.author.id,
                channel_name=maybe(message).channel.name.or_else(None),
                parent_channel_name=maybe(message).channel.parent.name.or_else(None),
                guild_name=maybe(message).guild.name.or_else(None),
                created_at=message.created_at,
            ),
        )
        # sample: {"ts":"2023-08-11 17:32:20.496","module":"listen_to_discord","message":{"id":1139612279776751756,"jump_url":"https://discord.com/channels/1106702799938519211/1139612279776751756/1139612279776751756","content":"pongpong","type":["default",0],"author_name":"marklidenberg","author_global_name":"Mark Lidenberg","author_display_name":"Mark Lidenberg","author_id":913095424225706005,"channel_name":"ping","parent_channel_name":"marklidenberg-and-his-bot-discussions","guild_name":"Engineering Friends","created_at":"2023-08-11 17:32:20.471000+00:00"}}

        # - Filter forum post messages: from forum channel and is starter message

        if self.filter_forum_post_messages:
            is_post_message = isinstance(
                maybe(message).channel.parent.or_else(None), discord.ForumChannel
            ) and message.id == maybe(message).channel.starter_message.id.or_else(None)

            logger.info("is_post_message", value=is_post_message)

            if not is_post_message:
                return

        # - Get image attachments

        filename_urls = [
            attachment.url
            for attachment in message.attachments
            if maybe(attachment).url.or_else(None) and maybe(attachment).filename.or_else(None)
        ]

        # - Fix usernames in message text and replace with display names

        for user_id in re.findall(r"<@(\d+)>", message.content):  # <@913095424225706005>
            # - Get user

            user = message.guild.get_member(int(user_id))

            # - Replace <@913095424225706005> with <name>

            message.content = message.content.replace(f"<@{user_id}>", user.nick or user.global_name)

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

            message.content = message.content.replace(f"<@&{role_id}>", f"@{role.name}")

        # - Send post to telegram

        try:
            await self.process_message(
                channel_name=maybe(message).channel.name.or_else(""),
                parent_channel_name=maybe(message).channel.parent.name.or_else(""),
                title=maybe(message).channel.name.or_else(""),
                body=message.content,
                author_name=message.author.display_name,
                url=message.jump_url,
                files=filename_urls,
            )
        except:
            logger.exception("Failed to forward message")


async def test():
    # - Define process_discord_post

    async def process(**kwargs):
        logger.info("Processing discord post", **kwargs)

    # - Init client

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = OnMessageDiscordClient(
        process_message=process,
        intents=intents,
    )

    # - Run main

    async with client:
        await client.start(token=config.discord_token)


if __name__ == "__main__":
    configure_loguru()
    asyncio.run(test())
