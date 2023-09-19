import asyncio

from functools import partial

import discord
import openai

from discord_to_telegram_forwarder.config.config import config
from discord_to_telegram_forwarder.on_message_discord_client import OnMessageDiscordClient
from discord_to_telegram_forwarder.send_discord_post_to_telegram.send_discord_post_to_telegram import (
    send_discord_post_to_telegram,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.update_telegram_post import update_telegram_post
from discord_to_telegram_forwarder.telegram_client import telegram_client
from pymaybe import maybe

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru


# - Configure openai api key

openai.api_key = config.openai_api_key

# - Init discord client


async def process_message(message):
    await send_discord_post_to_telegram(
        message=message,
        telegram_chat_to_filter={
            config.telegram_ef_discussions: lambda message: maybe(message).channel.category.name.or_else("")
            == "Discussions"
            and message.guild.name == config.guild_name,
            config.telegram_ef_channel: lambda message: maybe(message).channel.category.name.or_else("")
            != "Discussions"
            and message.guild.name == config.guild_name,
        },
        filter_forum_post_messages=config.filter_forum_post_messages,
    ),
    await update_telegram_post(message),


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
client = OnMessageDiscordClient(
    process_message=process_message,
    intents=intents,
)

# - Run main


async def main():
    # - Start telegram client

    await telegram_client.start()

    # - Start discord client

    async with client:
        await client.start(token=config.discord_token)


if __name__ == "__main__":
    configure_loguru()
    asyncio.run(main())
