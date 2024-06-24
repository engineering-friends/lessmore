import asyncio
import json

from datetime import datetime
from pathlib import Path

from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.file_primitives.write_file import write_file
from telegram_playground.deps import Deps
from telethon import TelegramClient


UNARCHIVED = 0
ARCHIVED = 1


async def main():
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

    dialogs = await client.get_dialogs(archived=False)

    # - Dump file

    write_file(
        data={dialog.id: dialog.name for dialog in dialogs},
        filename=Path(__file__).parent / f"../data/dynamic/archived-chats-{datetime.now().isoformat()}.json",
        writer=lambda data, filename: json.dump(data, filename, indent=4, default=str, ensure_ascii=False),
    )

    # - Archive all dialogs

    for dialog in dialogs:
        await client.edit_folder(entity=dialog.id, folder=ARCHIVED)


if __name__ == "__main__":
    asyncio.run(main())
