import asyncio

from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from loguru import logger
from telethon import TelegramClient
from telethon_playground.deps.deps import Deps


async def clean_saved_messages(telegram_client: TelegramClient):
    # - Get my id
    me = await telegram_client.get_me()

    # - Remove all "saved messages"

    async for message in telegram_client.iter_messages(entity=me):
        await telegram_client.delete_messages(entity=me, message_ids=[message.id])
        await asyncio.sleep(0.5)


def test():
    async def main():
        await clean_saved_messages(await Deps.load(env="test").started_telegram_user_client())

    asyncio.run(main())


if __name__ == "__main__":
    test()
