import asyncio

from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest


async def add_user_to_chats(
    telegram_client: TelegramClient,
    chats: list[str | int],
    username: str,
):
    # Get the channel and user objects
    user = await telegram_client.get_entity(f"@{username.replace('@', '')}")

    for chat in chats:
        logger.info("Inviting user to chat", chat=chat, user=user)
        await telegram_client(
            InviteToChannelRequest(
                channel=await telegram_client.get_entity(chat),
                users=[user],
            )
        )


def test():
    async def main():
        from ef_bots.ef_org_bot.ef_org_bot import EFOrgBot

        async with EFOrgBot().stack() as (ef_bot, app):
            await add_user_to_chats(
                telegram_client=ef_bot.telegram_user_client,
                chats=ef_bot.config.telegram_ef_chats.values(),
                username="@lidenberg",
            )

    asyncio.run(main())


if __name__ == "__main__":
    test()
