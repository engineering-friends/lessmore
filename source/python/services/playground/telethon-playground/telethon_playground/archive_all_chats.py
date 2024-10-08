import asyncio

from telethon import TelegramClient
from telethon_playground.deps.deps import Deps


async def archive_all_chats(client: TelegramClient):
    async for dialog in client.iter_dialogs():
        if not dialog.archived:
            await client.edit_folder(entity=dialog, folder=1)


def test():
    async def main():
        deps = Deps.load(env="test")
        await archive_all_chats(await deps.started_telegram_user_client())

    asyncio.run(main())


if __name__ == "__main__":
    test()
