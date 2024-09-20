import asyncio
import json
import os
import re

from dataclasses import dataclass, field

from aiogram.types import BotCommand
from ef_bots.ef_threads.app import App, User
from ef_bots.ef_threads.deps.deps import Deps
from ef_bots.ef_threads.parse_telegram_username_by_whois_url import parse_telegram_username_by_whois_url
from lessmore.utils.file_primitives.read_file import read_file
from lessmore.utils.file_primitives.write_file import write_file
from loguru import logger
from telethon import TelegramClient, events, types


def main(env="test"):
    async def _main():
        # - Init deps

        deps = Deps.load(env=env)

        # - Start client

        client: TelegramClient = deps.telegram_user_client
        await client.start()

        print("Listening for new messages in the discussion group...")

        # - Init app

        app = App()
        app.load_state()

        # - Define lock

        locks_by_user_id: dict[int, asyncio.Lock] = dict()

        # - Define handler

        @client.on(events.NewMessage(chats=deps.config.telegram_discussion_group))
        async def on_message(event):
            async with locks_by_user_id.get(event.message.input_sender.user_id, asyncio.Lock()):
                # - Unfold messages

                new_message = event.message

                # - Return if not a reply to any post

                if not new_message.reply_to_msg_id:
                    logger.debug("This message is not a reply to any post.", message_id=new_message.id)

                # - Get original message with thread id (original message id)

                original_message = await client.get_messages(
                    deps.config.telegram_discussion_group, ids=new_message.reply_to_msg_id
                )

                thread_id = original_message.id

                # - Get the message title

                title = original_message.text.split("\n")[0].replace("**", "").strip()

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
                    notion_client=deps.notion_client(),
                    telegram_usernames_by_notion_whois_url=app.telegram_usernames_by_notion_whois_url,
                    last_checked_telegram_username_at_by_notion_whois_url=app.last_checked_telegram_username_at_by_notion_whois_url,
                )

                if telegram_username:
                    telegram_usernames.append(telegram_username)

                # --- - Tags

                for telegram_username in re.findall(r"@(\w+)", new_message.text):
                    telegram_usernames.append(telegram_username)

                # --- Get user ids by telegram usernames

                for telegram_username in telegram_usernames:
                    try:
                        input_entity = await deps.telegram_user_client.get_input_entity(telegram_username)
                        user_ids.append(input_entity.user_id)
                    except:
                        logger.error("Failed to get input entity", telegram_username=telegram_username)

                logger.debug("User ids", user_ids=user_ids, telegram_usernames=telegram_usernames)

                # -- Filter only test users

                user_ids = [
                    user_id for user_id in user_ids if user_id in [160773045, 291560340, 407931344]
                ]  # marklidenberg, petr lavrov, mikhail vodolagin

                # -- Subscribe users, who sent the message, to the thread

                for user_id in user_ids:
                    if user_id not in app.users:
                        app.users[user_id] = User(id=user_id)

                    user = app.users[user_id]
                    user.thread_ids = list(set(user.thread_ids + [thread_id]))

                # - Send message to all subscribed users

                for user in app.users.values():
                    if thread_id in user.thread_ids:
                        if user.current_thread_id != thread_id:
                            message = await client.send_message(
                                entity=user.id,
                                message=f"[{title}](https://t.me/c/{str(deps.config.telegram_discussion_group)[4:]}/{new_message.id}?thread={thread_id})",
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
                        message = await client.forward_messages(
                            entity=user.id,
                            messages=new_message.id,
                            from_peer=deps.config.telegram_discussion_group,
                        )
                        user.thread_id_by_message_id[message.id] = thread_id

                # - Dump state

                app.dump_state()

        # - Subscribe to emoji reactions

        @client.on(events.Raw)
        async def handler(event):
            if isinstance(event, types.UpdateEditMessage):
                async with locks_by_user_id.get(event.message.chat_id, asyncio.Lock()):
                    # - Get chat id

                    chat_id = event.message.chat_id
                    message_id = event.message.id
                    reactions = event.message.reactions

                    user = app.users.get(chat_id)
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
                        await client.delete_messages(chat_id, message_id_to_remove)

                    # - Dump state

                    app.dump_state()

        # - Run client

        await client.run_until_disconnected()

    asyncio.run(_main())


if __name__ == "__main__":
    import fire

    fire.Fire(main)
