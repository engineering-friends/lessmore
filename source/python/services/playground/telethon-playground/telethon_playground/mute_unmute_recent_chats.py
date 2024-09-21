import asyncio

from datetime import datetime, timedelta

from lessmore.utils.to_anything.to_datetime import to_datetime
from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerNotifySettings
from telethon_playground.deps.deps import Deps


async def mute_unrecent_chats(telegram_client: TelegramClient, offset: timedelta = timedelta(hours=4)):
    # - Get my id

    me = await telegram_client.get_me()

    # - Process chats

    async for dialog in telegram_client.iter_dialogs():
        logger.info(f"Processing chat: {dialog.title}")

        # - Skip muted chats

        if not dialog.dialog.notify_settings.mute_until or dialog.dialog.notify_settings.mute_until.replace(
            tzinfo=None
        ) != to_datetime("1970.01.01"):
            logger.info(f"Skipping muted chat: {dialog.title}")
            continue

        # - Get the chat history

        # -- Get message that was sent 4 hours ago

        history = await telegram_client(
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
        if not history.messages:
            continue

        start_id = history.messages[-1].id + 1

        # -- Get the chat history

        history = await telegram_client(
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

        has_recent_messages = False

        for message in history.messages:
            if message.sender_id == me.id:  # Check if the message is from us
                if to_datetime("now") - offset < message.date.replace(
                    tzinfo=None
                ):  # Check if the message is within the last 4 hours
                    has_recent_messages = True
                    break

        # - Mute or unmute the chat based on message presence

        if has_recent_messages:
            logger.info(f"Skipping chat: {dialog.title}, because it has recent messages")
            continue

        # - Mute the chat indefinitely

        await telegram_client(
            UpdateNotifySettingsRequest(
                peer=dialog.entity,
                settings=InputPeerNotifySettings(mute_until=2**31 - 1),  # Mute indefinitely
            )
        )
        print(f"Muted chat: {dialog.title}")


def test():
    async def main():
        await mute_unrecent_chats(await Deps.load(env="test").started_telegram_user_client())

    asyncio.run(main())


if __name__ == "__main__":
    test()
