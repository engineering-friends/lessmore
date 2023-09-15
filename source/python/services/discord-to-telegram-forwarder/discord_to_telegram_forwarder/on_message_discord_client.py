import asyncio

from typing import Callable

import discord
from box import Box

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
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.process_message = process_message

    async def on_ready(self):
        logger.info(f"Logged in", user=self.user, id=self.user.id)

    async def on_message(self, message: discord.Message):
        try:
            # - Log

            logger.info('Received message', message=message)

            # - Process message

            await self.process_message(message)
        except Exception as e:
            logger.exception(e)


async def test():
    # - Define process_discord_post

    async def process_message(message):
        logger.info("Processing discord post", message=message)

    # - Init client

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = OnMessageDiscordClient(
        process_message=process_message,
        intents=intents,
    )

    # - Run main

    async with client:
        await client.start(token=config.discord_token)


if __name__ == "__main__":
    configure_loguru()
    asyncio.run(test())
