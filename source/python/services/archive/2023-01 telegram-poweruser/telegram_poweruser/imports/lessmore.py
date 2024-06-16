from telegram_poweruser.imports.external import *  # isort: skip

# - Missing dependencies


# -- NotionClient

import os

from dateutil.parser import parse
from notion_client import Client


class Page:
    """
    Page example: {"object": "page", "id": "1fb4ac4d-e2b1-42d5-9465-be9050c03e18", "created_time": "2022-08-14T19:28:00.000Z", "last_edited_time": "2022-08-14T19:28:00.000Z", "created_by": {"object": "user", "id": "bdb47407-ca48-4745-9aff-74763ad1bae0"}, "last_edited_by": {"object": "user", "id": "bdb47407-ca48-4745-9aff-74763ad1bae0"}, "cover": null, "icon": null, "parent": {"type": "database_id", "database_id": "099ac8c2-8f16-451d-bf99-274ef93aef7b"}, "archived": false, "properties": {"\\u0422\\u043e\\u043f\\u0438\\u043a\\u0438": {"id": "roMA", "type": "relation", "relation": [{"id": "02c88eba-4e51-4675-a9cd-2db50e16fa2b"}]}, "Name": {"id": "title", "type": "title", "title": [{"type": "text", "text": {"content": "\\u0421\\u0435\\u043c\\u044c\\u044f", "link": null}, "annotations": {"bold": false, "italic": false, "strikethrough": false, "underline": false, "code": false, "color": "default"}, "plain_text": "\\u0421\\u0435\\u043c\\u044c\\u044f", "href": null}]}}, "url": "https://www.notion.so/1fb4ac4de2b142d59465be9050c03e18"}
    """

    def __init__(self, info):
        self.info = info

    @property
    def title(self):
        try:
            title_property = [p for p in self.info["properties"].values() if p["type"] == "title"][0]
            return title_property["title"][0]["plain_text"]
        except:
            # untitled
            return ""

    def __getitem__(self, item):
        return self.info[item]


class NotionClient(Client):
    def query_database_pages(self, database_id, filter=None, sorts=None):
        result = []
        start_cursor = None
        while True:
            response = self.databases.query(
                database_id, start_cursor=start_cursor, filter=filter, sorts=sorts, page_size=100
            )
            result += response["results"]

            if response["next_cursor"] is None:
                break
            else:
                start_cursor = response["next_cursor"]

        result = [self.cast_page(page_info) for page_info in result]

        # filter untitled pages
        result = [page for page in result if page.title]
        return result

    def get_database_last_edit_time(self, database_id):
        pages = self.query_database_pages(database_id)
        database = self.databases.retrieve(database_id)
        return parse(max([page["last_edited_time"] for page in pages] + [database["last_edited_time"]])).replace(
            tzinfo=None
        )

    def cast_page(self, page_info):
        if "object" not in page_info:
            # fetch page if only id is provided in info
            assert len(page_info.keys()) == 1 and list(page_info.keys())[0] == "id"
            page_info = self.pages.retrieve(page_id=page_info["id"])
        return Page(page_info)

    def get_page_property(self, page, property):
        if property not in page["properties"]:
            raise Exception(f"Property {property} not found")

        property_type = page["properties"][property]["type"]
        if property_type == "relation":
            return [self.cast_page(page_info) for page_info in page["properties"][property]["relation"]]
        elif property_type == "rich_text":
            return page["properties"][property]["rich_text"][0]["plain_text"]
        elif property_type == "title":
            return page["properties"][property]["title"][0]["plain_text"]
        else:
            raise Exception(f"Type {property_type} not supported yet")


# -- TelegramClient

import asyncio
import json
import os

from datetime import datetime, timedelta, timezone
from functools import cached_property
from pprint import pprint
from typing import Literal

import cachetools

from bidict import bidict
from loguru import logger
from path import Path
from telethon import TelegramClient as TelethonTelegramClient, events, functions, hints, types
from telethon.tl.functions.messages import GetAllStickersRequest, GetStickerSetRequest
from telethon.tl.types import InputStickerSetID


# - Utils


async def custom_apply_recursively_async(value, f, *args, **kwargs):
    if isinstance(value, dict):
        if "InputPeer" in str(value.get("_")):
            return await f(value, *args, **kwargs)
        else:
            return {k: await custom_apply_recursively_async(v, f, *args, **kwargs) for k, v in value.items()}
    elif isinstance(value, list):
        return [await custom_apply_recursively_async(v, f, *args, **kwargs) for v in value]
    elif isinstance(value, set):
        return {await custom_apply_recursively_async(v, f, *args, **kwargs) for v in value}
    elif isinstance(value, tuple):
        return tuple(await custom_apply_recursively_async(v, f, *args, **kwargs) for v in value)
    else:
        return await f(value, *args, **kwargs)


# - Globals

lock = asyncio.Lock()

# - Client


class TelegramClient(TelethonTelegramClient):
    """Custom extension over TelethonTelegramClient"""

    def __init__(
        self,
        throttle_period_in_seconds=60,
        throttle_max_count=60,
        is_disabled_after_throttling=True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # - Input arguments

        self.throttle_period_in_seconds = throttle_period_in_seconds
        self.throttle_max_count = throttle_max_count
        self.disable_after_throttling = is_disabled_after_throttling

        # - Throttling state

        self._is_throttling = False
        self._throttle_ttl_cache = cachetools.TTLCache(
            maxsize=1_000_000, ttl=self.throttle_period_in_seconds
        )  # {request_date: 1} (note: 1 is a stub, list would be better here but I don't have implementation at hand)

        # - Message cache

        self.message_cache = cachetools.FIFOCache(maxsize=10_000)  # {(chat_id, message_id): message_text}

        # - Dialog_title by key_id

        self.dialog_title_by_key_id = bidict({})

    # Throttle all requests to some reasonable amount
    async def __call__(self, *args, **kwargs):
        # - Check if throttling is active

        if self.disable_after_throttling and self._is_throttling:
            raise Exception("Client disabled because of throttling")

        # - Check for throttle

        if len(self._throttle_ttl_cache) >= self.throttle_max_count:  # no more than 60 requests per minute
            if self.disable_after_throttling:
                self._is_throttling = True
            raise Exception("Request throttled")

        # - Fill request to cache

        self._throttle_ttl_cache[datetime.now()] = 1

        # - Execute request

        return await super().__call__(*args, **kwargs)

    async def get_peer_title(self, peer):
        # - Cast peer

        peer = await self.cast_peer(peer)

        # - Get entity

        entity = self.get_entity(peer)

        # - Return entity title

        return self.get_entity_title(entity)

    @staticmethod
    def get_message_key(message):
        # - Get media id

        media_id = (
            get_complex_attribute(message, "media.id", is_safe=True)
            or get_complex_attribute(message, "media.photo.id", is_safe=True)
            or ""
        )

        # - Return key

        return "-".join([str(message.raw_text), str(media_id)])

    async def search_message(self, peer, message_key, max_period=timedelta(days=7)):
        """Find message by key"""

        # - Iterate over recent message till we find the message

        async for message in self.iter_messages(peer):
            # - Check if our message

            if self.get_message_key(message) == message_key:
                return message

            # - Check if too late

            if message.date.replace(tzinfo=None) < datetime.utcnow() - max_period:
                break

        return None

    async def get_dialog_filters(self):
        """Get dialog filters (folders)."""
        return await self(functions.messages.GetDialogFiltersRequest())

    async def get_dialog_filter(self, title):
        for dialog_filter in await self.get_dialog_filters():
            if dialog_filter.title == title:
                return dialog_filter

    @property
    async def real_self_peer(self):
        me = await self.get_entity("me")
        return types.InputPeerUser(user_id=me.id, access_hash=me.access_hash)

    async def cast_peer(
        self,
        peer_like: hints.EntityLike
        | types.InputPeerSelf
        | types.InputPeerUser
        | types.InputPeerChannel
        | types.InputPeerChat,
    ):
        """Cast peer"""
        if isinstance(peer_like, types.InputPeerSelf):
            return await self.real_self_peer
        elif isinstance(peer_like, (types.InputPeerUser, types.InputPeerChannel, types.InputPeerChat)):
            return peer_like
        else:
            input_entity = await self.get_input_entity(peer_like)

            # apply to_peer once again to InputPeerSelf to convert to real self peer
            return await self.cast_peer(input_entity)

    async def add_chats_to_folder(self, peers, folder_title):
        # - Cast peers

        peers = [await self.cast_peer(peer_value) for peer_value in peers]

        # - Load current dialog filter

        dialog_filter = await self.get_dialog_filter(folder_title)

        # - Add new peers

        added_peers = []
        for peer in peers:
            if any(
                peer == dialog_peer
                for dialog_peer in dialog_filter.include_peers
                + dialog_filter.exclude_peers
                + dialog_filter.pinned_peers
            ):
                # - Already in folder in some position

                continue

            added_peers.append(peer)
            dialog_filter.include_peers.append(peer)

        # - Check if no update needed

        if not added_peers:
            logger.info("Chats are already in folder or excluded", folder_title=folder_title, peers=peers)
            return []

        # - Update Dialog Filter

        await self(functions.messages.UpdateDialogFilterRequest(id=dialog_filter.id, filter=dialog_filter))

        # - Return added chat ids

        return added_peers

    async def remove_chats_from_folder(self, peers, folder_title):
        # - Cast peers

        peers = [await self.cast_peer(peer_value) for peer_value in peers]
        logger.info("Removing chats from folder", folder_title=folder_title, peers=peers)  # fmt: skip

        # - Get current dialog filter

        dialog_filter = await self.get_dialog_filter(folder_title)

        # - Calculate removed chat ids. If chat is pinned or excluded, it will be considered as already removed

        removed_peers = [
            peer for peer in peers if any(peer == dialog_peer for dialog_peer in dialog_filter.include_peers)
        ]

        # - Filter peers

        if not removed_peers:
            logger.info("Chats already not in folder", folder_title=folder_title, peers=peers)
            return []

        dialog_filter.include_peers = [peer for peer in dialog_filter.include_peers if peer not in removed_peers]

        # - Update dialog filter

        await self(functions.messages.UpdateDialogFilterRequest(id=dialog_filter.id, filter=dialog_filter))

        # - Return removed chat ids

        return removed_peers

    async def create_channel(self, title, about="..."):
        logger.info("Creating channel", title=title, about=about)
        return await self(functions.channels.CreateChannelRequest(title=title, about=about))

    async def delete_channel(self, channel_peer):
        # - Cast peer

        channel_peer = await self.cast_peer(channel_peer)

        # - Delete channel

        logger.info("Deleting channel", channel_peer=channel_peer)
        return await self(functions.channels.DeleteChannelRequest(channel_peer))

    async def export_folders(self, folder_sessions_directory="folder_sessions"):
        # - Init paths

        session_name = unified_datetime.to_filename_safe_string(datetime.now())
        os.makedirs(Path(folder_sessions_directory) / session_name)

        # - Iterate over folders and export them

        for dialog_filter in await self.get_dialog_filters():
            logger.info("Processing", dialog_filter=dialog_filter)

            # - Convert to dict

            folder_info = dialog_filter.to_dict()

            # - Add chat name to peers for readability

            async def _add_custom_fields(value):
                logger.info("Adding custom fields", value=value)
                if not isinstance(value, dict) or "InputPeer" not in str(value.get("_")):
                    return value
                else:
                    try:
                        # dict with InputPeer* key
                        result = dict(value)

                        cls_name = result["_"]
                        keyword_arguments = {k: v for k, v in value.items() if k != "_"}
                        peer = get_complex_attribute(types, cls_name)(**keyword_arguments)
                        result["custom__entity_title"] = self.get_entity_title(await self.get_entity(peer))
                        result["custom__peer_id"] = await self.get_peer_id(peer)
                        return result
                    except:
                        logger.error("Failed to process channel", value=value)
                        return value

            # - Add

            folder_info = await custom_apply_recursively_async(folder_info, _add_custom_fields)

            # - Dump

            with open(
                Path(folder_sessions_directory)
                / session_name
                / (dialog_filter.title + "-" + str(dialog_filter.id) + ".json"),
                "w",
            ) as f:
                f.write(json.dumps(folder_info, indent=4, ensure_ascii=False))

    async def import_folder(self, folder_dump_filename):
        # - Load folder info

        with open(folder_dump_filename) as f:
            folder_info = json.loads(f.read())

        # - Init dialog_filter

        dialog_filter = types.DialogFilter(
            id=folder_info["id"],
            title=folder_info["title"],
            include_peers=[
                await self.get_input_entity(peer["custom__peer_id"]) for peer in folder_info["include_peers"]
            ],
            exclude_peers=[
                await self.get_input_entity(peer["custom__peer_id"]) for peer in folder_info["exclude_peers"]
            ],
            pinned_peers=[await self.get_input_entity(peer["custom__peer_id"]) for peer in folder_info["pinned_peers"]],
        )

        # - Update dialog filter

        return await self(functions.messages.UpdateDialogFilterRequest(id=dialog_filter.id, filter=dialog_filter))

    async def mute_chat(self, peer):
        # - Cast peer

        peer = await self.cast_peer(peer)
        logger.info("Muting chat", peer=peer)

        # - Create settings

        notify_settings = await self(functions.account.GetNotifySettingsRequest(peer=peer))

        # _  Return if already muted
        if notify_settings.mute_until or notify_settings.silent:
            logger.info("Chat already muted", peer=peer)
            return True

        # - Mute

        return await self(
            functions.account.UpdateNotifySettingsRequest(
                peer=types.InputNotifyPeer(peer),
                settings=types.InputPeerNotifySettings(
                    silent=notify_settings.silent,
                    mute_until=datetime(2038, 1, 19, 3, 14, 7, tzinfo=timezone.utc),
                    sound=notify_settings.sound or "default",
                    show_previews=notify_settings.show_previews,
                ),
            )
        )

    async def unmute_chat(self, peer):
        # - Cast peer

        peer = await self.cast_peer(peer)
        logger.info("Unmuting chat", peer=peer)

        # - Create settings

        notify_settings = await self(functions.account.GetNotifySettingsRequest(peer=peer))

        # - Return if already unmuted

        if not notify_settings.mute_until and not notify_settings.silent:
            logger.info("Chat already unmuted", peer=peer)
            return True

        # - Unmute

        return await self(
            functions.account.UpdateNotifySettingsRequest(
                peer=types.InputNotifyPeer(peer),
                settings=types.InputPeerNotifySettings(
                    silent=notify_settings.silent,
                    mute_until=None,
                    sound=notify_settings.sound or "default",
                    show_previews=notify_settings.show_previews,
                ),
            )
        )

    async def get_trail_messages(self, peer, max_period=timedelta(days=30), max_messages=200):
        """Get message trail (their last messages + one my last message)"""

        # - Cast peer

        peer = await self.cast_peer(peer)

        # - Get recent message till my first one

        async def trail_condition_to_stop(current_messages, new_message):
            if current_messages and current_messages[-1].out:
                return True
            return False

        return await self.get_recent_messages(
            peer, max_messages=max_messages, max_period=max_period, condition_to_stop=trail_condition_to_stop
        )

    async def get_recent_messages(self, peer, condition_to_stop=None, max_period=timedelta(days=7), max_messages=None):
        # - Cast peer

        peer = await self.cast_peer(peer)

        # - Prepare condition to stop

        basic_limits_condition_to_stop = None
        if max_period or max_messages:
            assert max_period or max_messages

            async def basic_limits_condition_to_stop(current_messages, new_message):
                if max_period:
                    if new_message.date.replace(tzinfo=None) < datetime.utcnow() - max_period:
                        # failed to find my message, trail is not relevant
                        return True
                if max_messages:
                    if len(current_messages) == max_messages:
                        return True

                return False

        # - Iterate

        result = []
        async for message in self.iter_messages(peer):
            assert condition_to_stop or basic_limits_condition_to_stop
            if condition_to_stop and await condition_to_stop(current_messages=result, new_message=message):
                break

            if basic_limits_condition_to_stop and await basic_limits_condition_to_stop(
                current_messages=result, new_message=message
            ):
                break

            result.append(message)

        return result

    def get_entity_type(self, entity: hints.EntityLike) -> Literal["bot", "user", "group", "channel"]:
        if isinstance(entity, (types.UserEmpty, types.User)):
            if entity.bot:
                return "bot"
            else:
                return "user"
        elif isinstance(entity, (types.ChatEmpty, types.Chat, types.ChatForbidden)):
            return "group"
        elif isinstance(entity, (types.Channel, types.ChannelForbidden)):
            if entity.megagroup or entity.gigagroup:
                return "group"
            else:
                return "channel"
        else:
            raise Exception("Unknown entity type")

    async def get_sticker_documents(self, sticker_set_title, sticker_document_ids=None):
        # - Get sticker set

        all_sticker_sets = (await self(GetAllStickersRequest(0))).sets

        if sticker_set_title not in [sticker_set.title for sticker_set in all_sticker_sets]:
            raise Exception(f"Sticker set not found: {sticker_set_title}")

        sticker_set = [sticker_set for sticker_set in all_sticker_sets if sticker_set.title == sticker_set_title][0]

        # - Get all sticker documents

        sticker_documents = (
            await self(
                GetStickerSetRequest(
                    stickerset=InputStickerSetID(id=sticker_set.id, access_hash=sticker_set.access_hash)
                )
            )
        ).documents

        # - Filter stocker documents if needed

        if sticker_document_ids:
            sticker_documents = [
                [doc for doc in sticker_documents if doc.id == sticker_document_id][0]
                for sticker_document_id in sticker_document_ids
            ]

        return sticker_documents

    async def get_dialogs_by_condition(self, condition_to_stop=None, **kwargs):
        result = []

        async for dialog in self.iter_dialogs(**kwargs):
            # - Filter no-title dialogs

            if not dialog.title:
                continue

            # - Check if break needed

            if condition_to_stop and await condition_to_stop(result, dialog):
                break

            result.append(dialog)

        return result

    def get_entity_title(self, entity: hints.EntityLike):
        """Get entity title (chat name)
        == dialog.title in all cases I've found"""
        try:
            if entity.title:
                return entity.title
        except:
            pass

        try:
            res = ""
            if entity.first_name:
                res += str(entity.first_name) + " "
            if entity.last_name:
                res += str(entity.last_name)
            res = res.strip()
            if res:
                return res  # Ivan Novikov
        except:
            pass

        raise Exception(f"Failed to find entity title: {entity.id}")
