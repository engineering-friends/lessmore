import os

import discord
import keyring

from loguru import logger

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru
from lessmore.utils.encoding.encode_to_pickle import encode_to_pickle
from lessmore.utils.file_helpers.write_file import write_file


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged on as", self.user)

    async def on_message(self, message: discord.message.Message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        write_file(content=encode_to_pickle(message, library="dill"), filename="message.pkl")

        logger.info(
            "Received message",
            message=dict(
                id=message.id,
                jump_url=message.jump_url,
                content=message.content,
                type=message.type,
                author_name=message.author.name,
                author_global_name=message.author.global_name,
                author_display_name=message.author.display_name,
                author_id=message.author.id,
                channel_name=message.channel.name,
                parent_channel_name=message.channel.parent.name,
                guild_name=message.guild.name,
                created_at=message.created_at,
            ),
        )


if __name__ == "__main__":
    configure_loguru()
    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(keyring.get_password(service_name="discord", username="marklidenberg-bot"))
