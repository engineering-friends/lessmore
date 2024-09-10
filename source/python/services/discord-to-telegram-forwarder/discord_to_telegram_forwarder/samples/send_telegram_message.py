import asyncio

from discord_to_telegram_forwarder.deps import Deps


async def main():
    # - Init deps

    deps = Deps.load()

    # - Start telegram bots

    await deps.telegram_user_client.start()

    # - Send message

    await deps.telegram_user_client.send_message(
        entity="marklidenberg",
        message="# Test \n ## Test \n ### Test   ",
        file=["send_telegram_message.py"],  # works with files or urls
        parse_mode="md",
    )


if __name__ == "__main__":
    asyncio.run(main())
