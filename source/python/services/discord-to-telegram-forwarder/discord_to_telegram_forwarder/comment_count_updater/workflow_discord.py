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
        process_message: Callable,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.process_message = process_message

    async def on_ready(self):
        logger.info(f"Logged in", user=self.user, id=self.user.id)

        all_channels = self.get_all_channels()

        channel = self.get_channel()
        if not channel:
            await ctx.send("Channel not found.")
            return

        async for message in channel.history(limit=1000):  # Adjust the limit if needed
            if query in message.content:
                await ctx.send(f"Found in message by {message.author}: {message.content}")
                break
        else:
            await ctx.send("Message not found.")


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

    # async with client:
    #     await client.start(token=config.discord_token)

    # - Search message in discord with title "Notion мощно обновил свои формулы, я как-то не заметил"

    async with client:
        await client.start(token=config.discord_token)


if __name__ == "__main__":
    configure_loguru()
    asyncio.run(test())
