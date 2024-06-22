import asyncio
import json

from pathlib import Path

from telegram_playground.deps import Deps
from telethon import TelegramClient


async def main():
    # - Init deps

    deps = Deps.load()

    # - Init client

    telegram_client = TelegramClient(
        session=str(Path(__file__).parent / "telegram.session"),
        api_id=int(deps.config.telegram_api_id),
        api_hash=deps.config.telegram_api_hash,
    )

    # - Login

    await telegram_client.start(bot_token=deps.config.telegram_bot_token)

    # - Get me

    print(
        await telegram_client.get_me()
    )  # User(id=5661836491, is_self=True, contact=False, mutual_contact=False, deleted=False, bot=True, bot_chat_history=False, bot_nochats=False, verified=False, restricted=False, min=False, bot_inline_geo=False, support=False, scam=False, apply_min_photo=True, fake=False, access_hash=8294607786604554060, first_name='channeled_sharing_bot', last_name=None, username='channeled_sharing_bot', phone=None, photo=None, status=None, bot_info_version=1, restriction_reason=[], bot_inline_placeholder=None, lang_code=None)

    # - Send message

    await telegram_client.send_message(
        entity="marklidenberg",
        message="# Test \n ## Test \n ### Test   ",
        file=["send_telegram_message.py"],  # works with files or urls
        parse_mode="md",
    )


if __name__ == "__main__":
    asyncio.run(main())
