import asyncio

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest


def purge_telegram_chat(chat: str, api_id: int, api_hash: str):
    async def delete_saved_messages(client: TelegramClient):
        # - Get peer by chat name

        entity = await client.get_entity(chat)

        # - Delete messages

        # Keep track of the last message ID we've seen, start with 0
        last_message_id = 0

        while True:
            print("Retrieving...")
            history = await client(
                GetHistoryRequest(
                    peer=entity,
                    offset_id=last_message_id,
                    limit=100,  # You can fetch up to 100 messages at a time
                    add_offset=0,
                    offset_date=None,
                    max_id=0,
                    min_id=0,
                    hash=0,
                )
            )

            # If there are no more messages, break the loop
            if not history.messages:
                break

            # Delete fetched messages
            await client.delete_messages(entity=entity, message_ids=[msg.id for msg in history.messages])

            # Update the last message ID
            last_message_id = history.messages[-1].id

            # Sleep is optional, to ensure you're not rate-limited
            await asyncio.sleep(1)  # Be respectful of Telegram's server

    # Connect to the client
    with TelegramClient("purge_telegram_chat", api_id=api_id, api_hash=api_hash) as client:
        client.loop.run_until_complete(delete_saved_messages(client))


if __name__ == "__main__":
    purge_telegram_chat(chat="marklidenberg", api_id=123456, api_hash="1234567890abcdef1234567890abcdef")
