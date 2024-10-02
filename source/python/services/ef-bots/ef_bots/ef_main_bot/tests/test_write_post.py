import asyncio

from ef_bots.ef_main_bot.ef_main_bot import EfMainBot


async def test_write_post():
    async with EfMainBot.stack(env="test") as (ef_main_bot, app):
        await app.run(starters={ef_main_bot.deps.config.telegram_test_chat_id: ef_main_bot.test})


if __name__ == "__main__":
    asyncio.run(test_write_post())
