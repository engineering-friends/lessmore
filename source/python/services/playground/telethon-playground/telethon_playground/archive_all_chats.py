import asyncio

from telethon import TelegramClient
from telethon_playground.deps.deps import Deps


def test():
    async def main():
        deps = Deps.load(env="test")

        # - Start client

        client: TelegramClient = deps.telegram_user_client
        await client.start()

        # - Archive all chats

        for dialog in await client.get_dialogs():
            await client.edit_folder(entity=dialog, folder=1)

    asyncio.run(main())


if __name__ == "__main__":
    test()
