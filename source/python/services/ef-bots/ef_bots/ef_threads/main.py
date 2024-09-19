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
from telethon import TelegramClient, events


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

        lock = asyncio.Lock()  # process only one message at a time

        # - Define handler

        @client.on(events.NewMessage(chats=deps.config.telegram_discussion_group))
        async def on_message(event):
            async with lock:
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

                # -- Subscribe users, who sent the message, to the thread

                for user_id in user_ids:
                    if user_id not in app.users_by_id:
                        app.users.append(User(id=user_id))

                        user = app.users_by_id[user_id]
                        user.thread_ids = list(set(user.thread_ids + [thread_id]))

                # - Send message to all subscribed users

                for user in app.users:
                    if thread_id in user.thread_ids:
                        if user.current_thread_id != thread_id:
                            message = await client.send_message(
                                entity=user.id,
                                message=f"{'—' * 15}\n[{title}](https://t.me/c/{str(deps.config.telegram_discussion_group)[4:]}/{thread_id}){'—' * 15}\n",
                            )
                            user.first_thread_message_id = message.id

                        await client.forward_messages(
                            entity=user.id,
                            messages=new_message.id,
                            from_peer=deps.config.telegram_discussion_group,
                        )
                    user.current_thread_id = thread_id

                # - Dump state

                app.dump_state()

        # - Run client

        await client.run_until_disconnected()

    asyncio.run(_main())


if __name__ == "__main__":
    import fire

    fire.Fire(main)
