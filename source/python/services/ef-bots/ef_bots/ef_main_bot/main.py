import asyncio

from aiogram.types import BotCommand
from ef_bots.ef_main_bot.ef_main_bot import EfOrgBot
from loguru import logger
from pymaybe import maybe


async def main(env: str):
    async with EfOrgBot.stack(env=env) as (ef_main_bot, app):
        # - Load chat_ids to run at startup - the ones which have last message from the bot (usually the menu message). Needed for user not to press /start if bot has been restarted, and just used the menu of the last message (beta)

        chat_ids_to_run_at_startup = [
            chat_id
            for chat_id, chat_private_state in app.iter_chat_states(private=True)
            if maybe(chat_private_state)["messages"][-1]["from_user"]["is_bot"].or_else(False)
        ]

        logger.info("Chats to run at startup", chat_ids=chat_ids_to_run_at_startup)

        # - Start polling

        await app.run(
            starters={
                chat_id: lambda response: response.ask(ef_main_bot.menu, mode="inplace_latest")
                for chat_id in chat_ids_to_run_at_startup
            },  # in case of restart, we will start from the last bot message
            command_starters={"/start": lambda response: response.ask(ef_main_bot.menu)},
            commands=[
                BotCommand(command="start", description="Start the bot"),
                BotCommand(command="cancel", description="Cancel the current operation"),
            ],
        )


if __name__ == "__main__":
    import fire

    def sync_main(env: str = "test"):
        asyncio.run(main(env=env))

    fire.Fire(sync_main)
