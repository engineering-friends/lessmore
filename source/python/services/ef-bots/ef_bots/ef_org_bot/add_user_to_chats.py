import asyncio

from ef_bots.ef_org_bot.deps import Deps
from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest


async def add_user_to_chats(
    telegram_client: TelegramClient,
    username: str,
    chats: list[str | int],
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


async def test():
    async with Deps() as deps:
        await add_user_to_chats(
            telegram_client=deps.telegram_user_client,
            chats=[-1002219948749],  # ef test chat
            username="@lidenberg",
        )


if __name__ == "__main__":
    asyncio.run(test())
