import asyncio

from datetime import datetime, timedelta

from lessmore.utils.to_anything.to_datetime import to_datetime
from loguru import logger
from sympy import limit
from telethon import TelegramClient, events, types
from telethon.tl import functions
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerNotifySettings
from telethon_playground.deps.deps import Deps


async def download_chat_messages(client: TelegramClient, limit: int = 100):
    # - Get my id

    me = await client.get_me()

    # - Process chats

    async for dialog in client.iter_dialogs():
        logger.trace("Processing chat", chat_title=dialog.title)

        # - Skip me

        if dialog.entity.id == me.id:
            logger.trace("Skipping me", chat_title=dialog.title)
            continue

        # - Skip muted chats

        if dialog.dialog.notify_settings.mute_until and dialog.dialog.notify_settings.mute_until.replace(
            tzinfo=None
        ) != to_datetime("1970.01.01"):
            logger.trace("Skipping muted chat", chat_title=dialog.title)
            continue

        # - Get if has recent messages

        has_recent_messages = False

        # -- Get message that was sent 4 hours ago

        history = await client(
            GetHistoryRequest(
                peer=dialog.entity,
                limit=1,
                offset_date=to_datetime("now") - timedelta(hours=4),
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0,
            )
        )

        if history.messages:
            start_id = history.messages[-1].id + 1

            # -- Get the chat history

            history = await client(
                GetHistoryRequest(
                    peer=dialog.entity,
                    limit=0,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=start_id,
                    add_offset=0,
                    hash=0,
                )
            )

            # - Flag to determine if we have any recent messages

            for message in history.messages:
                if message.sender_id == me.id:  # Check if the message is from us
                    if to_datetime("now") - offset < message.date.replace(
                        tzinfo=None
                    ):  # Check if the message is within the last 4 hours
                        has_recent_messages = True
                        break

        # - Mute or unmute the chat based on message presence

        if has_recent_messages:
            logger.trace("No recent messages", chat_title=dialog.title)
            continue

        # - Mute the chat indefinitely

        await client(
            UpdateNotifySettingsRequest(
                peer=dialog.entity,
                settings=InputPeerNotifySettings(mute_until=2**31 - 1),  # Mute indefinitely
            )
        )

        await asyncio.sleep(
            5
        )  # to avoid rate limit (a rough estimate is around 30 requests per minute, in practice not enough)
        logger.debug("Muted chat", chat_title=dialog.title)


async def download_chat_messages(client: TelegramClient, limit: int = 100):
    pass


def test():
    async def main():
        # - Get telegram client

        client = await Deps.load(env="test").started_telegram_user_client()

        # - Start the client

        await download_chat_messages(client, limit=100)

        # - Start polling

        await client.run_until_disconnected()

    asyncio.run(main())


if __name__ == "__main__":
    test()
