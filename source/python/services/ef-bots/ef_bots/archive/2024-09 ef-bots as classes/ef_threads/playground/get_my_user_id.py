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

        # - Send message

        await client.send_message(
            entity="marklidenberg",
            message="[URL](https://t.me/c/2219948749/84?thread=81)",
            parse_mode="markdown",
        )

    asyncio.run(main())


if __name__ == "__main__":
    test()
