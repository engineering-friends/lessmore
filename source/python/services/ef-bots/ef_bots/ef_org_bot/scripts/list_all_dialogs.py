import asyncio

from ef_bots.ef_org_bot.deps.deps import Deps


def list_all_dialogs():
    async def main():
        # - Init deps

        deps = Deps.load()

        # - Start user

        await deps.telegram_user_client.start()

        # - Iterate over dialogs

        async for dialog in deps.telegram_user_client.iter_dialogs():
            print(dialog.title, dialog.id)

    asyncio.run(main())


if __name__ == "__main__":
    list_all_dialogs()
