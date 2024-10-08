import asyncio

from typing import Literal

import discord

from discord_to_telegram_forwarder.deps import Deps
from discord_to_telegram_forwarder.on_message_discord_client import OnMessageDiscordClient
from discord_to_telegram_forwarder.send_discord_post_to_telegram.send_discord_post_to_telegram import (
    send_discord_post_to_telegram,
)
from discord_to_telegram_forwarder.update_comments_counter.update_comments_counter import update_comments_counter
from loguru import logger
from pymaybe import maybe


async def main(env: Literal["test", "prod"] = "test"):
    logger.info("Starting discord-to-telegram-forwarder", env=env)

    # - Init deps

    deps = Deps.load(env=env)

    # - Define `process_message` function

    async def process_message(message: discord.Message):
        # - Post message

        await send_discord_post_to_telegram(
            deps=deps,
            message=message,
            telegram_chat_to_filter={
                deps.config.telegram_ef_channel: lambda message: "dont_forward_to_tg"
                not in [tag.name for tag in maybe(message).channel.applied_tags.or_else([])]
                and message.guild.name == deps.config.guild_name,
            },
        )

        # - Update comments counter

        await update_comments_counter(
            deps=deps,
            message=message,
            channels=[deps.config.telegram_ef_channel],
        )

    # - Init a discord client

    client = OnMessageDiscordClient(process_message=process_message)

    # - Start telegram clients

    await deps.telegram_bot_client.start(bot_token=deps.config.telegram_bot_token)
    await deps.telegram_user_client.start()

    # - Start the discord client

    async with client:
        await client.start(token=deps.config.discord_token)


if __name__ == "__main__":
    asyncio.run(main())
