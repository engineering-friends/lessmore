import asyncio

import discord
import openai

from discord_to_telegram_forwarder.config.config import config
from discord_to_telegram_forwarder.on_message_discord_client import OnMessageDiscordClient
from discord_to_telegram_forwarder.send_discord_post_to_telegram.send_discord_post_to_telegram import (
    send_discord_post_to_telegram,
)
from discord_to_telegram_forwarder.telegram_clients.telegram_bot_client import telegram_bot_client
from discord_to_telegram_forwarder.telegram_clients.telegram_user_client import telegram_user_client
from discord_to_telegram_forwarder.update_comments_counter import update_comments_counter
from pymaybe import maybe

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru


# - Configure openai api key

openai.api_key = config.openai_api_key

# - Define process_message function


async def process_message(message: discord.Message):
    # - Post message

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
    )

    # - Update comments counter

    await update_comments_counter(
        message=message, channels=[config.telegram_ef_discussions, config.telegram_ef_channel]
    )


# - Init discord client

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
    # - Start telegram clients

    await telegram_bot_client.start(bot_token=config.telegram_bot_token)
    await telegram_user_client.start()

    # - Start discord client

    async with client:
        await client.start(token=config.discord_token)


if __name__ == "__main__":
    configure_loguru()
    asyncio.run(main())
