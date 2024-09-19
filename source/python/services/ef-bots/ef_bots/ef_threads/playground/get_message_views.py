import asyncio

from ef_bots.ef_threads.deps.deps import Deps
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetMessagesViewsRequest
from telethon.tl.types import InputChannel, InputMessageID


def test():
    async def main():
        # - Init deps

        deps = Deps.load()

        # - Start user

        await deps.telegram_user_client.start()

        # - Get message views

        # Get the input channel (replace channel_id with the real channel id or username)
        channel = await deps.telegram_user_client.get_entity(-1001897462358)  # EF Test

        # Fetch the views for the message (replace message_id with the message's id)
        result = await deps.telegram_user_client(
            GetMessagesViewsRequest(
                peer=channel,
                id=[2],  # You can pass multiple message IDs in this list
                increment=False,  # Set this to True if you want to increase the view count
            )
        )

        pass

    asyncio.run(main())


if __name__ == "__main__":
    test()
