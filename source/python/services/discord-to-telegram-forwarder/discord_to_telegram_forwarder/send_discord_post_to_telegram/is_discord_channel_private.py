import asyncio

import discord


def is_discord_channel_private(channel: discord.abc.GuildChannel) -> bool:
    for overwrite_type, overwrite in channel.overwrites.items():
        if isinstance(overwrite_type, (discord.Role, discord.Member)):
            if overwrite.read_messages is False:
                return True
    return False


async def test():
    from discord_to_telegram_forwarder.config.config import config

    class MyClient(discord.Client):
        async def on_ready(self):
            print("Logged on as", self.user)

            for guild in self.guilds:
                for channel in guild.text_channels:
                    print(channel.name, is_discord_channel_private(channel))

                for channel in guild.forums:
                    print(channel.name, is_discord_channel_private(channel))

    # - Init client

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = MyClient(intents=intents)

    # - Run main

    async with client:
        await client.start(token=config.discord_token)


if __name__ == "__main__":
    asyncio.run(test())
