import asyncio
import json

from datetime import datetime
from pathlib import Path

from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.file_primitives.read_file import read_file
from telegram_playground.deps import Deps
from telethon import TelegramClient
from telethon.tl.types import PeerUser


UNARCHIVED = 0
ARCHIVED = 1


async def unarchive(dialog_ids_path: str):
    # - Init deps

    deps = Deps.load()

    # - Init client

    client = TelegramClient(
        session=str(ensure_path(Path(__file__).parent / "../data/dynamic/telegram_user.session")),
        api_id=int(deps.config.telegram_api_id),
        api_hash=deps.config.telegram_api_hash,
    )

    # - Login

    await client.start()

    # - Get all non-archived dialogs

    dialog_ids = read_file(
        dialog_ids_path,
        reader=json.load,
    )

    if isinstance(dialog_ids, dict):
        dialog_ids = list(dialog_ids.keys())

    # - Load dialogs to fill cache

    await client.get_dialogs()

    # - Archive all dialogs

    for dialog_id in dialog_ids:
        await client.edit_folder(entity=int(dialog_id), folder=UNARCHIVED)


if __name__ == "__main__":
    asyncio.run(
        unarchive(
            dialog_ids_path=str(
                Path(__file__).parent / "../data/dynamic/archived-chats-2024-06-22T12:43:04.412113.json"
            )
        )
    )
