import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession


async def init_and_print_session():
    # - Init client

    session = StringSession()
    client = TelegramClient(
        session=session,
        api_id=int("<API_ID>"),
        api_hash="<API_HASH>",
    )
    await client.start()

    # - Print info about me

    print((await client.get_me()).stringify())

    print(session.save())


async def test_session():
    # - Init client

    # SHOULD NOT REQUEST PASSWORD THIS TIME

    session = StringSession("<YOUR_SESSION>")
    client = TelegramClient(
        session=session,
        api_id=int("<API_ID>"),
        api_hash="<API_HASH>",
    )
    await client.start()

    # - Print info about me

    print((await client.get_me()).stringify())


if __name__ == "__main__":
    asyncio.run(init_and_print_session())
    asyncio.run(test_session())
