import asyncio

from ef_bots.ef_threads.deps.deps import Deps
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetMessageReadParticipantsRequest, GetMessagesViewsRequest
from telethon.tl.types import (
    InputChannel,
    InputMessageID,
    InputPeerChannel,
    InputPeerChat,
    InputPeerUser,
    PeerChannel,
    PeerChat,
    ReadParticipantDate,
)


def test():
    async def main():
        # - Init deps

        deps = Deps.load()

        # - Start user

        await deps.telegram_user_client.start()

        # - Get message views

        group = await deps.telegram_user_client.get_entity(-1001980795916)  # EF Test

        # - Get last message in the group

        messages = await deps.telegram_user_client.get_messages(group, limit=1)

        result: list[ReadParticipantDate] = await deps.telegram_user_client(
            GetMessageReadParticipantsRequest(
                peer=group,
                msg_id=messages[0].id,
            )
        )

        for value in result:
            print(value)

    asyncio.run(main())


if __name__ == "__main__":
    test()
