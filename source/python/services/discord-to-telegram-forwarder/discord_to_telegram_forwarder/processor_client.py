import asyncio

from typing import Callable

import discord

from discord_to_telegram_forwarder.config.config import config
from loguru import logger
from pymaybe import maybe

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru


# - Init discord client


class ProcessorClient(discord.Client):
    def __init__(
        self,
        *args,
        process_discord_post: Callable,
        filter_forum_post_messages: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.process_discord_post = process_discord_post
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

        image_urls = [
            attachment.url
            for attachment in message.attachments
            if attachment.url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"))
        ]

        # - Send post to telegram

        try:
            await self.process_discord_post(
                post_forum_channel_name=maybe(message).channel.parent.name.or_else(""),
                post_title=maybe(message).channel.name.or_else(""),
                post_body=message.content,
                post_author_name=message.author.display_name,
                post_url=message.jump_url,
                files=image_urls,
            )
        except:
            logger.exception("Failed to forward message")


async def test():
    # - Define process_discord_post

    async def process_discord_post(**kwargs):
        logger.info("Processing discord post", **kwargs)

    # - Init client

    intents = discord.Intents.default()
    intents.message_content = True
    client = ProcessorClient(
        process_discord_post=process_discord_post,
        intents=intents,
    )

    # - Run main

    async with client:
        await client.start(token=config.discord_token)


if __name__ == "__main__":
    configure_loguru()
    asyncio.run(test())
