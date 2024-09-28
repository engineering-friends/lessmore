import asyncio

from ef_bots.ef_org_bot.main import EFOrgBot


async def test_start_onboarding():
    async with EFOrgBot().stack() as (ef_bot, app):
        await app.run(starters={ef_bot.config.telegram_test_chat_id: ef_bot.start_onboarding})


if __name__ == "__main__":
    asyncio.run(test_start_onboarding())
