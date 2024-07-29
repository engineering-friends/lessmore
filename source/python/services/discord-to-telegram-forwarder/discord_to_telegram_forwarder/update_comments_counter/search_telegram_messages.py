from discord_to_telegram_forwarder.deps import Deps
from telethon.tl.patched import Message


async def search_telegram_messages(
    deps: Deps,
    channel: str | int,
    query: str,
) -> list[Message]:
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

    deps = Deps.load(log_level="TRACE")

    # - Start telegram client

    await deps.telegram_user_client.start()

    # - Search messages

    print(await search_telegram_messages(deps=deps, channel=-1001897462358, query="Foo by Mark Lidenberg"))
    print(await search_telegram_messages(deps=deps, channel=-1001897462358, query="Foo by Mark Lidenberg"))
    print("cache", deps.cache)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test())
