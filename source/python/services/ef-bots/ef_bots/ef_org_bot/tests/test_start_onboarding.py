import asyncio

from ef_bots.ef_org_bot.main import EfOrgBot


async def test_start_onboarding():
    async with EfOrgBot().stack() as (ef_org_bot, app):
        await app.run(starters={ef_org_bot.config.telegram_test_chat_id: ef_org_bot.start_onboarding})


if __name__ == "__main__":
    asyncio.run(test_start_onboarding())
