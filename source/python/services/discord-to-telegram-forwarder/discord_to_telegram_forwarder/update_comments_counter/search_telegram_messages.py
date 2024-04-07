from discord_to_telegram_forwarder.deps.deps import Deps
from discord_to_telegram_forwarder.deps.init_deps import init_deps
from telethon.tl.patched import Message


async def search_telegram_messages(deps: Deps, channel: str | int, query: str) -> list[Message]:
    # - Set cache key

    cache_key = ("search_telegram_messages", channel, query)

    # - Set value in cache if not exists

    if cache_key not in deps.cache:
        deps.cache[cache_key] = [
            message async for message in deps.telegram_user_client.iter_messages(channel, search=query)
        ]

    # - Return value from cache

    return deps.cache[cache_key]


async def test():
    # - Init deps

    deps = init_deps(log_level="TRACE")

    # - Start telegram client

    await deps.telegram_bot_client.start()

    # - Search messages

    # todo later: if >1 files - pick out gifs and send separately [@marklidenberg]
    await deps.telegram_bot_client.send_message(
        entity=-1001897462358,
        message="hello",
        parse_mode="md",
        link_preview=False,
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(test())
