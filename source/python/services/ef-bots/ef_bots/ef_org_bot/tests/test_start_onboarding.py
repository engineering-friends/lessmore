import asyncio

from ef_bots.ef_org_bot.main import EFOrgBot
from teletalk.app import App
from teletalk.models.response import Response


def test_start_onboarding():
    async def _main():
        async with EFOrgBot().stack() as (ef_bot, app):
            await app.start_polling(
                bot=ef_bot.config.telegram_bot_token,
                initial_starters={ef_bot.config.telegram_test_chat_id: ef_bot.start_onboarding},
            )

    asyncio.run(_main())


if __name__ == "__main__":
    test_start_onboarding()
