import asyncio

from telethon import TelegramClient


def test():
    async def main():
        from ef_bots.ef_threads.deps import Deps

        async with Deps(env="test") as deps:
            await deps.telegram_user_client.start()
            input_entity = await deps.telegram_user_client.get_input_entity("marklidenberg")
            print(input_entity)

    asyncio.run(main())


if __name__ == "__main__":
    test()
