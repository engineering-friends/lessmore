import asyncio

from datetime import datetime, timedelta

from lessmore.utils.to_anything.to_datetime import to_datetime
from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerNotifySettings
from telethon_playground.deps.deps import Deps


async def mute_unmute_recent_chats(telegram_client: TelegramClient):
    # - Get my id

    me = await telegram_client.get_me()

    # - Process chats

    async for dialog in telegram_client.iter_dialogs():
        # - Unfold chat

        chat = dialog.entity

        logger.info(f"Processing chat: {dialog.title}")

        # - Get the chat history

        history = await telegram_client(
            GetHistoryRequest(
                peer=chat,
                limit=100,  # Checking up to 100 messages for efficiency
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0,
            )
        )

        # - Flag to determine if we have any recent messages

        has_recent_messages = False

        for message in history.messages:
            if message.from_id.user_id == me.id:  # Check if the message is from us
                if to_datetime("now") - timedelta(hours=4) < message.date.replace(
                    tzinfo=None
                ):  # Check if the message is within the last 4 hours
                    has_recent_messages = True
                    break

        # - Mute or unmute the chat based on message presence

        if has_recent_messages:
            # - Unmute the chat

            await telegram_client(
                UpdateNotifySettingsRequest(
                    peer=chat,
                    settings=InputPeerNotifySettings(mute_until=None),  # Unmute the chat
                )
            )
            print(f"Unmuted chat: {dialog.title}")
        else:
            # - Mute the chat indefinitely

            await telegram_client(
                UpdateNotifySettingsRequest(
                    peer=chat,
                    settings=InputPeerNotifySettings(mute_until=2**31 - 1),  # Mute indefinitely
                )
            )
            print(f"Muted chat: {dialog.title}")

        break


def test():
    async def main():
        await mute_unmute_recent_chats(await Deps.load(env="test").started_telegram_user_client())

    asyncio.run(main())


if __name__ == "__main__":
    test()
