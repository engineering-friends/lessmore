import asyncio

from typing import Callable

import discord

from discord_to_telegram_forwarder.deps import Deps
from loguru import logger


# - Init discord client


class OnMessageDiscordClient(discord.Client):
    def __init__(
        self,
        process_message: Callable,
        **kwargs,
    ):
        self.process_message = process_message
        super().__init__(
            intents=discord.Intents.all(),  # request all intents for simplicity
            **kwargs,
        )

    async def on_ready(self):
        logger.info("Logged in", user=self.user, id=self.user.id)

    async def on_message(self, message: discord.Message):
        try:
            # - Log

            logger.info("Received message", message=message)

            # - Process message

            await self.process_message(message=message)
        except Exception as e:
            logger.exception(e)


async def test():
    # - Init deps

    deps = Deps.load()

    # - Define `process_message`

    async def process_message(message):
        logger.info("Processing discord post", message=message)

    # - Init client

    client = OnMessageDiscordClient(process_message=process_message)

    # - Run main

    async with client:
        await client.start(token=deps.config.discord_token)


if __name__ == "__main__":
    asyncio.run(test())
