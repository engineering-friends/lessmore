import asyncio

from telethon import TelegramClient
from telethon_playground.deps.deps import Deps


def test():
    async def main():
        deps = Deps.load(env="test")

        # - Start client

        client: TelegramClient = deps.telegram_user_client
        await client.start()

        # - Get my id

        me = await client.get_me()

        # - Remove all "saved messages"

        async for message in client.iter_messages(entity=me):
            await client.delete_messages(entity=me, message_ids=[message.id])
            await asyncio.sleep(0.5)

    asyncio.run(main())


if __name__ == "__main__":
    test()
