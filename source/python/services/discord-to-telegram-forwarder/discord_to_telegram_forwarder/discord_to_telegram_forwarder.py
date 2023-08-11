import asyncio
import random

import discord
import keyring
import openai

from discord import Client
from loguru import logger
from pymaybe import maybe
from telethon import TelegramClient

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru
from lessmore.utils.encoding.decode_from_json import decode_from_json
from lessmore.utils.file_helpers.read_file import read_file
from lessmore.utils.path_helpers.get_current_dir import get_current_dir


# - Init discord client

intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)

# - Init telegram client


# - Init client

telegram_client = TelegramClient(
    session=str(get_current_dir() / "../data/dynamic/telegram.session"),
    api_id=decode_from_json(keyring.get_password(service_name="telegram", username="channeled-sharing-bot"))["api_id"],
    api_hash=decode_from_json(keyring.get_password(service_name="telegram", username="channeled-sharing-bot"))[
        "api_hash"
    ],
)


@client.event
async def on_ready():
    logger.info(f"Logged in", user=client.user, id=client.user.id)


@client.event
async def on_message(message):
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

    # - Read emoticons

    emoticons = read_file("emoticons.txt").strip().split("\n")

    # - Parse message a bit

    parent_channel_name = maybe(message).channel.parent.name.or_else("")
    channel_name = maybe(message).channel.name.or_else(None)

    # - Get emoji from openai

    # openai.api_key = keyring.get_password(service_name="openai", username="channeled-sharing-bot")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"I want you to respond in a single emoji, one symbol. It should represent the following text: {parent_channel_name}\n{channel_name}\n{message.content}",
            },
        ],
    )
    emoji = response.choices[0].message.content

    # - Format message for telegram

    parent_channel_name = maybe(message).channel.parent.name.or_else("")
    channel_name = maybe(message).channel.name.or_else(None)
    text = ""
    if parent_channel_name:
        text += f"#{parent_channel_name}\n"

    text += f"{emoji} **{channel_name}**\n\n"
    text += message.content + "\n\n"

    text += f"[→ к посту {random.choice(emoticons)}]({message.jump_url})"

    # - Send message to telegram

    await telegram_client.send_message(entity="marklidenberg", message=text, parse_mode="md", link_preview=False)


async def main():
    # - Start telegram client

    await telegram_client.start(
        bot_token=decode_from_json(keyring.get_password(service_name="telegram", username="channeled-sharing-bot"))[
            "bot_token"
        ]
    )

    # - Start discord client

    async with client:
        await client.start(token=keyring.get_password(service_name="discord", username="marklidenberg-bot"))


if __name__ == "__main__":
    configure_loguru()
    asyncio.run(main())
