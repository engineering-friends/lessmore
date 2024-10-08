import asyncio

from telethon import TelegramClient


def test():
    async def main():
        from ef_bots.ef_threads.deps import Deps

        async with Deps(env="test") as deps:
            await deps.telegram_user_client.send_message(
                entity="marklidenberg",
                message="[URL](https://t.me/c/2219948749/84?thread=81)",
                parse_mode="markdown",
            )

    asyncio.run(main())


if __name__ == "__main__":
    test()
