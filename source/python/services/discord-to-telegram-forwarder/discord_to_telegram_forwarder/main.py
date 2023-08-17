import asyncio

from functools import partial

import discord
import openai

from discord_to_telegram_forwarder.config.config import config
from discord_to_telegram_forwarder.on_message_discord_client import OnMessageDiscordClient
from discord_to_telegram_forwarder.send_discord_post_to_telegram.send_discord_post_to_telegram import (
    send_discord_post_to_telegram,
)
from discord_to_telegram_forwarder.telegram_client import telegram_client

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru


# - Configure openai api key

openai.api_key = config.openai_api_key

# - Init discord client

intents = discord.Intents.default()
intents.message_content = True
client = OnMessageDiscordClient(
    process_message=partial(
        send_discord_post_to_telegram,
        telegram_chat=config.telegram_chat,
    ),
    filter_forum_post_messages=config.filter_forum_post_messages,
    intents=intents,
)

# - Run main


async def main():
    # - Start telegram client

    await telegram_client.start(bot_token=config.telegram_bot_token)

    # - Start discord client

    async with client:
        await client.start(token=config.discord_token)


if __name__ == "__main__":
    configure_loguru()
    asyncio.run(main())
