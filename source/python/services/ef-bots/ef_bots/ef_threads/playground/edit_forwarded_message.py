import asyncio

from telethon import TelegramClient


def test():
    async def main():
        from ef_bots.ef_threads.deps import Deps

        async with Deps(env="test") as deps:
            # - Init client
            await deps.telegram_user_client.start()

            # - Get me

            me = await deps.telegram_user_client.get_me()

            # - Send test message

            message = await deps.telegram_user_client.send_message(
                entity=me.user_id,
                message="[URL](https://t.me/c/2219948749/84?thread=81)",
                parse_mode="markdown",
                reply_to_message_id=10,
            )

            # - Edit

    asyncio.run(main())


if __name__ == "__main__":
    test()
