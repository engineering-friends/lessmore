import asyncio

from aiogram.types import BotCommand
from ef_bots.ef_org_bot.deps.deps import Deps
from teletalk.app import App
from telethon import events


def main(env="test"):
    async def _main():
        # - Init deps

        deps = Deps.load(env=env)

        # - Start client

        client = deps.telegram_user_client
        await client.start()

        print("Listening for new messages in the discussion group...")

        # - Define handler

        # Listen to new messages in the discussion group
        @client.on(events.NewMessage(chats=deps.config.telegram_discussion_group))
        async def handler(event):
            # Get the new message text
            new_message = event.message
            print(f"New message: {new_message.text}")

            # Check if the message is a reply to a thread (has a reply_to_msg_id)
            if new_message.reply_to_msg_id:
                # Fetch the original post (message it's replying to)
                original_message = await client.get_messages(
                    deps.config.telegram_discussion_group, ids=new_message.reply_to_msg_id
                )
                print(f"Original post: {original_message.text}")
            else:
                print("This message is not a reply to any post.")

        # - Run client

        await client.run_until_disconnected()

    asyncio.run(_main())


if __name__ == "__main__":
    import fire

    fire.Fire(main)
