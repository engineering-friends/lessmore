import asyncio

from telethon import TelegramClient


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
            print(message.text)
            break

    asyncio.run(main())


if __name__ == "__main__":
    test()
