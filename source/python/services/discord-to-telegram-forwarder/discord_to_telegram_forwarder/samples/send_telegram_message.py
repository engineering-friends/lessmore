import asyncio

import keyring

from telethon import TelegramClient

from lessmore.utils.encoding.decode_from_json import decode_from_json
from lessmore.utils.path_helpers.get_current_dir import get_current_dir


async def main():
    # - Init client

    telegram_client = TelegramClient(
        session=str(get_current_dir() / "telegram.session"),
        api_id=decode_from_json(keyring.get_password(service_name="telegram", username="channeled-sharing-bot"))[
            "api_id"
        ],
        api_hash=decode_from_json(keyring.get_password(service_name="telegram", username="channeled-sharing-bot"))[
            "api_hash"
        ],
    )

    # - Login

    await telegram_client.start(
        bot_token=decode_from_json(keyring.get_password(service_name="telegram", username="channeled-sharing-bot"))[
            "bot_token"
        ]
    )

    # - Get me

    print(
        await telegram_client.get_me()
    )  # User(id=5661836491, is_self=True, contact=False, mutual_contact=False, deleted=False, bot=True, bot_chat_history=False, bot_nochats=False, verified=False, restricted=False, min=False, bot_inline_geo=False, support=False, scam=False, apply_min_photo=True, fake=False, access_hash=8294607786604554060, first_name='channeled_sharing_bot', last_name=None, username='channeled_sharing_bot', phone=None, photo=None, status=None, bot_info_version=1, restriction_reason=[], bot_inline_placeholder=None, lang_code=None)

    # - Send message

    await telegram_client.send_message(
        entity="marklidenberg",
        message="@marklidenberg",
        parse_mode="md",
    )


if __name__ == "__main__":
    asyncio.run(main())
