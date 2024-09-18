import asyncio

from ef_bots.ef_org_bot.deps.deps import Deps
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import Channel, Chat


async def add_user_to_chats(telegram_client, chats: list[str], username: str):
    # Get the channel and user objects
    user = await telegram_client.get_entity(f"@{username.replace('@', '')}")

    for chat in chats:
        # - Get entity
        entity = await telegram_client.get_entity(chat)

        # - If channel, invite user

        if isinstance(entity, Channel):
            await telegram_client(InviteToChannelRequest(channel=await telegram_client.get_entity(chat), users=[user]))

        # - If chat, invite user

        elif isinstance(entity, Chat):
            await telegram_client(Invite(channel=await telegram_client.get_entity(chat.id), users=[user]))


def test():
    async def main():
        # - Init deps

        deps = Deps.load()

        # - Start user

        await deps.telegram_user_client.start()

        # - Add to all telegram ecosystem: ef channel, ef random coffee

        await add_user_to_chats(
            telegram_client=deps.telegram_user_client,
            chats=deps.config.telegram_ef_chats.values(),
            username="@lidenberg",
        )

    asyncio.run(main())


if __name__ == "__main__":
    test()
