from telegram_poweruser.imports.runtime import *  # isort: skip


async def main():
    # - Init client

    telegram_client = TelegramClient(
        session=os.path.join(get_root_directory(__file__), "data/dynamic/telegram_sessions/channeled_sharing.session"),
        api_id=config.telegram_api_id,
        api_hash=config.telegram_api_hash,
    )

    await telegram_client.start()
    await telegram_client.export_folders(
        folder_sessions_directory=os.path.join(
            get_root_directory(__file__),
            "telegram_poweruser/microservices/export_import_folders/data/dynamic/folder_sessions",
        )
    )

    # await telegram_client.import_folder(
    #     "/Users/arsenijkadaner/Storage/Области/Разработка/projects/lessmore/family_fund.python/services/telegram-poweruser/data/dynamic/folder_sessions/2022.08.23-23_01_55/Test-3.json"
    # )


asyncio.run(main())
