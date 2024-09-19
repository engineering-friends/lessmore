import asyncio
import json
import os

from dataclasses import dataclass, field

from aiogram.types import BotCommand
from ef_bots.ef_threads.app import App, User
from ef_bots.ef_threads.deps.deps import Deps
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
        async def handler(event):
            async with lock:
                new_message = event.message

                if new_message.reply_to_msg_id:
                    # - Get original message

                    original_message = await client.get_messages(
                        deps.config.telegram_discussion_group, ids=new_message.reply_to_msg_id
                    )

                    thread_id = original_message.id

                    # - Get the message title

                    title = original_message.text.split("\n")[0].replace("**", "").strip()

                    # - Subscribe user, who sent the message, to the thread

                    user_id = new_message.input_sender.user_id
                    if user_id not in app.users_by_id:
                        app.users.append(User(id=user_id))

                    user = app.users_by_id[user_id]
                    user.thread_ids = list(set(user.thread_ids + [thread_id]))

                    # - Send message to all subscribed users

                    for user in app.users:
                        if thread_id in user.thread_ids:
                            if user.current_thread_id != thread_id:
                                await client.send_message(
                                    entity=user.id,
                                    message=f"{'—' * 15}\n[{title}](https://t.me/c/{str(deps.config.telegram_discussion_group)[4:]}/{thread_id}){'—' * 15}\n",
                                )

                            await client.forward_messages(
                                entity=user.id,
                                messages=new_message.id,
                                from_peer=deps.config.telegram_discussion_group,
                            )
                        user.current_thread_id = thread_id

                    # - Dump state

                    app.dump_state()

                else:
                    logger.debug("This message is not a reply to any post.", message_id=new_message.id)

        # - Run client

        await client.run_until_disconnected()

    asyncio.run(_main())


if __name__ == "__main__":
    import fire

    fire.Fire(main)
