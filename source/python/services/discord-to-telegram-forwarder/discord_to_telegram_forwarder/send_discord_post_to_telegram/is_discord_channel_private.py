import asyncio

import discord

from discord_to_telegram_forwarder.deps.init_deps import init_deps
from loguru import logger


def is_discord_channel_private(channel: discord.abc.GuildChannel) -> bool:
    for overwrite_type, overwrite in channel.overwrites.items():
        if isinstance(overwrite_type, (discord.Role, discord.Member)):
            if overwrite.read_messages is False:
                return True
    return False


async def test():
    # - Init deps

    deps = init_deps()

    class MyClient(discord.Client):
        async def on_ready(self):
            print("Logged on as", self.user)

            for guild in self.guilds:
                for channel in guild.text_channels:
                    logger.info(
                        "Text channel", channel_name=channel.name, is_private=is_discord_channel_private(channel)
                    )

                for channel in guild.forums:
                    logger.info("Forum", channel_name=channel.name, is_private=is_discord_channel_private(channel))

    # - Init client

    client = MyClient(intents=discord.Intents.all())

    # - Run main

    async with client:
        await client.start(token=deps.config.discord_token)


if __name__ == "__main__":
    asyncio.run(test())
