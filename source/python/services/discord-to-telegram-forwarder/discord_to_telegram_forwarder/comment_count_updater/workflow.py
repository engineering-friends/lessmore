# - Init client
from pathlib import Path

import keyring

from discord_to_telegram_forwarder.config.config import config
from telethon import TelegramClient

from lessmore.utils.encoding.decode_from_json import decode_from_json


# - Init client


async def main():
    telegram_client = TelegramClient(
        session=str(Path(__file__).parent / "telegram.session"),
        api_id=int(config.telegram_api_id),
        api_hash=config.telegram_api_hash,
    )

    await telegram_client.start()

    # - Loop over telegram chat -1001829309947 messages

    async for message in telegram_client.iter_messages("@marklidenberg"):
        print(message)
        print(message.text)

    # async for message in telegram_client.iter_messages(-1001829309947):
    #
    #     # - Parse text with regex: "... **(text)** ..." -> text
    #     import re
    #     title = re.search(r"\*\*(.*)\*\*", message.text).group(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
