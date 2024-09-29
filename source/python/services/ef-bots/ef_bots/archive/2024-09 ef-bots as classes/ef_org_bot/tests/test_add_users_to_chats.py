import asyncio

from ef_bots.ef_org_bot.ef_org_bot import EfOrgBot


async def test_add_user_to_chats():
    # - Init client

    async with EfOrgBot().stack() as (ef_org_bot, app):
        await ef_org_bot._add_user_to_chats(
            chats=[-1002219948749],  # ef test chat
            username="@lidenberg",
        )


if __name__ == "__main__":
    asyncio.run(test_add_user_to_chats())
