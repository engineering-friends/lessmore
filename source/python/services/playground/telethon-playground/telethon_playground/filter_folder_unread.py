import asyncio

from typing import Any

from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogFiltersRequest, UpdateDialogFilterRequest
from telethon.tl.types import DialogFilter, InputPeerChannel, InputPeerChat, InputPeerSelf
from telethon_playground.deps.deps import Deps


def get_entity_name(obj: Any) -> str:
    return (
        getattr(obj, "title")
        or getattr(obj, "username")
        or (getattr(obj, "first_name") or "" + getattr(obj, "last_name") or "")
        or str(obj.id)
    )


async def filter_folder_unread(client: TelegramClient, folder_name: str = "Groups"):
    logger.info("Filtering folder unread", folder_name=folder_name)

    # - Fetch all existing dialog folders

    filters = (await client(GetDialogFiltersRequest())).filters

    # - Find the specified folder by its name

    target_folder = next((f for f in filters if getattr(f, "title", "") == folder_name), None)

    if not target_folder:
        logger.error("Input folder not found", folder_name=folder_name)
        return

    logger.debug("Found input folder", folder_name=folder_name)

    # - Get new state of the folder

    updated_include = [InputPeerSelf()]  # need at least one chat in a folder
    updated_exclude = []

    all_dialogs = await client.get_dialogs(limit=20)

    for chat in target_folder.include_peers + target_folder.exclude_peers:
        entity = await client.get_entity(chat)

        dialog = next((d for d in all_dialogs if d.entity == entity), None)

        if not dialog:
            logger.debug("Dialog not found", chat_title=get_entity_name(entity))
            continue

        if dialog.unread_count == 0:
            logger.debug(
                "No unread messages found, excluding folder",
                chat_title=get_entity_name(entity),
            )
            updated_exclude.append(chat)
        else:
            logger.debug(
                "Unread messages found, including folder",
                chat_title=get_entity_name(entity),
            )
            updated_include.append(chat)

    # - Update the folder on Telegram

    await client(
        UpdateDialogFilterRequest(
            id=target_folder.id,
            filter=DialogFilter(
                id=target_folder.id,
                title=target_folder.title,
                include_peers=updated_include,
                exclude_peers=updated_exclude,
                pinned_peers=target_folder.pinned_peers,
                contacts=target_folder.contacts,
                non_contacts=target_folder.non_contacts,
                groups=target_folder.groups,
                broadcasts=target_folder.broadcasts,
                bots=target_folder.bots,
                exclude_muted=target_folder.exclude_muted,
                exclude_read=target_folder.exclude_read,
                exclude_archived=target_folder.exclude_archived,
            ),
        )
    )

    logger.debug("Updated folder", folder_name=folder_name)


def test():
    async def main():
        await filter_folder_unread(client=await Deps.load().started_telegram_user_client(), folder_name="Groups")

    asyncio.run(main())


if __name__ == "__main__":
    test()
