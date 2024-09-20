import asyncio

from ef_bots.ef_threads.deps.deps import Deps
from telethon import TelegramClient


def test():
    async def main():
        deps = Deps.load(env="test")

        # - Start client

        client: TelegramClient = deps.telegram_user_client
        await client.start()

        # - Get telegram username

        print((await deps.telegram_user_client.get_me()).id)

    asyncio.run(main())


if __name__ == "__main__":
    test()
