import asyncio
import re
import textwrap

from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import dacite

from aiogram.types import BotCommand
from ef_bots.ef_threads.deps import Deps
from ef_bots.ef_threads.parse_telegram_username_by_whois_url import parse_telegram_username_by_whois_url
from lessmore.utils.tested import tested
from loguru import logger
from pymaybe import maybe
from rocksdict import Rdict
from teletalk.app import App
from teletalk.models.response import Response
from telethon import events, types


if TYPE_CHECKING:
    from ef_bots.ef_threads.main import main


@dataclass
class User:
    id: int
    current_thread_id: int = 0
    current_thread_id_message_id: int = 0
    thread_ids: list[int] = field(default_factory=list)
    thread_id_by_message_id: dict[int, int] = field(default_factory=dict)
    enabled: bool = False


@dataclass
class AppState:
    users: dict[int, User] = field(default_factory=dict)


class EfThreads:
    def __init__(self, deps: Deps):
        # - Deps

        self.deps = deps

        # - State

        self.users: dict[int, User] = {}
        self.telegram_usernames_by_notion_whois_url: dict[str, str] = {}
        self.last_checked_telegram_username_at_by_notion_whois_url: dict[str, float] = {}
        self.rdict = Rdict(path=str(Path(__file__).parent / "state"))

    @staticmethod
    @asynccontextmanager
    async def stack(env: str):
        async with Deps(env=env) as deps:
            # - Init ef_threads

            ef_threads = EfThreads(deps=deps)

            # - Load state

            ef_threads.load_state()

            # - Return ef_threads

            try:
                yield ef_threads

            finally:
                # - Dump state

                ef_threads.dump_state()

    def load_state(self):
        self.users = dacite.from_dict(data_class=AppState, data=dict(self.rdict)).users

    def dump_state(self):
        # - Dump state

        for user in self.users.values():
            self.rdict[user.id] = user

        self.rdict.flush()

    @tested([main] if TYPE_CHECKING else [])
    async def run(self):
        # - Define lock

        locks_by_user_id: dict[int, asyncio.Lock] = dict()

        # - Define handler

        @self.deps.telegram_user_client.on(events.NewMessage(chats=self.deps.config.telegram_discussion_group))
        async def on_message(event):
            async with locks_by_user_id.get(event.message.input_sender.user_id, asyncio.Lock()):
                # - Unfold messages

                new_message = event.message

                # - Return if not a reply to any post

                if not new_message.reply_to_msg_id:
                    logger.debug("This message is not a reply to any post.", message_id=new_message.id)

                # - Get original message with thread id (original message id)

                original_message = await self.deps.telegram_user_client.get_messages(
                    self.deps.config.telegram_discussion_group, ids=new_message.reply_to_msg_id
                )

                thread_id = original_message.id

                # - Get the message title

                title = original_message.text.split("\n")[0].replace("**", "").strip()
                author = original_message.text.split("\n")[1].replace("**", "").replace("by", "").strip()

                # - Subscribe users to the thread

                # -- Collect users ids

                user_ids = []

                # --- Sender of the message

                user_ids.append(new_message.input_sender.user_id)

                # --- Telegram usernames

                # --- - Message author

                telegram_usernames = []

                telegram_username = await parse_telegram_username_by_whois_url(
                    text=new_message.text,
                    notion_client=self.deps.notion_client,
                    telegram_usernames_by_notion_whois_url=self.telegram_usernames_by_notion_whois_url,
                    last_checked_telegram_username_at_by_notion_whois_url=self.last_checked_telegram_username_at_by_notion_whois_url,
                )

                if telegram_username:
                    telegram_usernames.append(telegram_username)

                # --- - Tags

                for telegram_username in re.findall(r"@(\w+)", new_message.text):
                    telegram_usernames.append(telegram_username)

                # --- Get user ids by telegram usernames

                for telegram_username in telegram_usernames:
                    try:
                        input_entity = await self.deps.telegram_user_client.get_input_entity(telegram_username)
                        user_ids.append(input_entity.user_id)
                    except:
                        logger.error("Failed to get input entity", telegram_username=telegram_username)

                logger.debug("User ids", user_ids=user_ids, telegram_usernames=telegram_usernames)

                # -- Filter only test users

                user_ids = [
                    user_id for user_id in user_ids if user_id in [160773045, 291560340, 407931344, 1135785888]
                ]  # marklidenberg, petr lavrov, mikhail vodolagin, matvey mayakovskiy

                # -- Subscribe users, who sent the message, to the thread

                for user_id in user_ids:
                    if user_id not in self.users:
                        self.users[user_id] = User(id=user_id)

                    user = self.users[user_id]
                    user.thread_ids = list(set(user.thread_ids + [thread_id]))

                # - Send message to all subscribed users

                for user_id, user in self.users.items():
                    if not user.enabled:
                        # skip disabled users
                        continue

                    if thread_id in user.thread_ids or user_id == 160773045:
                        if user.current_thread_id != thread_id:
                            message = await self.deps.telegram_user_client.send_message(
                                entity=user.id,
                                message=f"**{title}**\nby {author}\n\nhttps://t.me/c/{str(self.deps.config.telegram_discussion_group)[4:]}/{new_message.id}?thread={thread_id}",
                            )
                            user.thread_id_by_message_id[message.id] = thread_id
                            user.current_thread_id_message_id = message.id
                            user.current_thread_id = thread_id

                        # todo maybe: update message text to reference LAST message in the thread [@marklidenberg]
                        # else:
                        #     if user.current_thread_id_message_id:
                        #         await client.edit_message(
                        #             message=user.current_thread_id_message_id,
                        #             entity=user.id,
                        #             text=f"[{title}](https://t.me/c/{str(deps.config.telegram_discussion_group)[4:]}/{new_message.id}?thread={thread_id})",
                        #         )
                        message = await self.deps.telegram_user_client.forward_messages(
                            entity=user.id,
                            messages=new_message.id,
                            from_peer=self.deps.config.telegram_discussion_group,
                        )
                        user.thread_id_by_message_id[message.id] = thread_id

                # - Dump state

                self.dump_state()

        # - Subscribe to emoji reactions

        @self.deps.telegram_user_client.on(events.Raw)
        async def handler(event):
            if isinstance(event, types.UpdateEditMessage):
                async with locks_by_user_id.get(event.message.chat_id, asyncio.Lock()):
                    # - Get chat id

                    chat_id = event.message.chat_id
                    message_id = event.message.id
                    reactions = event.message.reactions

                    user = self.users.get(chat_id)
                    if not user:
                        return

                    # - Get thread id

                    thread_id = user.thread_id_by_message_id.get(message_id)
                    if not thread_id:
                        return

                    # - Remove thread id from user

                    if thread_id in user.thread_ids:
                        user.thread_ids.remove(thread_id)

                    # - Remove message ids from that thread

                    # message_ids_to_remove = [_message_id for _message_id in  {k:v for k, v in user.thread_id_by_message_id.items() if v == thread_id}.keys() if _message_id >= message_id]
                    message_ids_to_remove = [
                        _message_id
                        for _message_id in {
                            k: v for k, v in user.thread_id_by_message_id.items() if v == thread_id
                        }.keys()
                    ]

                    logger.debug("Removing messages", message_ids=message_ids_to_remove)

                    for message_id_to_remove in message_ids_to_remove:
                        user.thread_id_by_message_id.pop(message_id_to_remove)
                        await self.deps.telegram_user_client.delete_messages(chat_id, message_id_to_remove)

                    # - Dump state

                    self.dump_state()

        # - Run simple teletalk app

        async def starter(response: Response):
            # - Add or get user

            user_id = response.message.from_user.id

            if user_id not in self.users:
                self.users[user_id] = User(id=user_id)
            user = self.users[user_id]

            # - Enable user

            user.enabled = True

            # - Send welcome message

            await response.tell(
                textwrap.dedent("""Привет!

Я буду пересылать комментарии на твои посты в канале EF Channel, а также на посты, в которых ты принимаешь участие.
        
Чтобы отписаться от поста, просто поставь **любую** реакцию на **любое** пересланное сообщение в **этом** чате 💥
        
Попробуй оставить комментарий, чтобы посмотреть как это работает: https://t.me/c/2219948749/187?thread=185""")
            )

            # - Dump state

            self.dump_state()

        asyncio.create_task(
            App(bot=self.deps.config.telegram_bot_token).run(
                command_starters={"/start": starter},
            )
        )

        # - Run telethon client

        await self.deps.telegram_user_client.run_until_disconnected()
