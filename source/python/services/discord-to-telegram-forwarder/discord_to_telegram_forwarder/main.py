import asyncio
import random

import discord
import openai

from discord import Client
from discord_to_telegram_forwarder.config.config import config
from discord_to_telegram_forwarder.send_telegram_post.send_discord_post_to_telegram import (
    request_emoji_from_openai,
    send_discord_post_to_telegram,
)
from discord_to_telegram_forwarder.telegram_client import telegram_client
from loguru import logger
from pymaybe import maybe

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru
from lessmore.utils.file_helpers.read_file import read_file
from lessmore.utils.path_helpers.get_current_dir import get_current_dir


# - Configure openai api key

openai.api_key = config.openai_api_key

# - Init discord client

intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)


@client.event
async def on_ready():
    logger.info(f"Logged in", user=client.user, id=client.user.id)


@client.event
async def on_message(message: discord.Message):
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

    is_post_message = isinstance(
        maybe(message).channel.parent.or_else(None), discord.ForumChannel
    ) and message.id == maybe(message).channel.starter_message.id.or_else(None)

    logger.info("is_post_message", value=is_post_message)

    if not is_post_message:
        return

    try:
        await send_discord_post_to_telegram(
            telegram_chat=config.telegram_chat,
            post_forum_channel_name=maybe(message).channel.parent.name.or_else(""),
            post_title=maybe(message).channel.name.or_else(""),
            post_body=message.content,
            post_url=message.jump_url,
        )
    except:
        logger.exception("Failed to forward message")


async def main():
    # - Start telegram client

    await telegram_client.start(bot_token=config.telegram_bot_token)

    # - Start discord client

    async with client:
        await client.start(token=config.discord_token)


if __name__ == "__main__":
    configure_loguru()
    asyncio.run(main())
