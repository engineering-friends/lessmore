import os

# init api callbacks
import telegram_poweruser.mini_apps.channeled_sharing.source.api_callbacks

from telegram_poweruser.mini_apps.channeled_sharing.source.bot_callbacks import build_application
from telegram_poweruser.mini_apps.channeled_sharing.source.notion_topics_syncer import start_notion_update_loop


# os.environ["telegram_poweruser_environment"] = "test"

from telegram_poweruser.mini_apps.channeled_sharing.imports.runtime import *  # isort: skip


async def main():
    # - Start telegram client

    logger.debug("Starting telegram client...", phone=config.telegram_phone)
    await telegram_client.start(phone=config.telegram_phone)
    logger.debug("Started telegram client", phone=config.telegram_phone)

    # - Setup notion loop coroutine

    loop = asyncio.get_event_loop()
    loop.create_task(start_notion_update_loop())

    # - Setup and run bot application

    bot_application = build_application()
    async with bot_application:
        await bot_application.start()
        logger.info("Started bot application")

        await bot_application.updater.run()
        logger.info("Started polling")

        await telegram_client.run_until_disconnected()
        logger.info("Disconnected")

        await bot_application.stop()
        logger.info("Stopped bot application")


if __name__ == "__main__":
    logger.info("Started channeled_sharing")

    asyncio.run(main())
