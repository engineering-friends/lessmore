import asyncio

from aiogram.types import BotCommand
from ef_bots.ef_org_bot.ef_org_bot import EFOrgBot
from loguru import logger
from pymaybe import maybe


def main(env="test"):
    async def async_main():
        async with EFOrgBot(env=env).stack() as (ef_bot, app):
            # - Load chat_ids to run at startup - the ones which have last message from the bot (usually the menu message). Needed for user not to press /start if bot has been restarted, and just used the menu of the last message (beta)

            chat_ids_to_run_at_startup = [
                chat_id
                for chat_id, chat_private_state in app.iter_chat_states(private=True)
                if maybe(chat_private_state)["messages"][-1]["from_user"]["is_bot"].or_else(False)
            ]

            logger.info("Chats to run at startup", chat_ids=chat_ids_to_run_at_startup)

            # - Start polling

            await app.start_polling(
                bot=ef_bot.config.telegram_bot_token,
                initial_starters={
                    chat_id: lambda response: response.ask(ef_bot.menu, mode="inplace_latest")
                    for chat_id in chat_ids_to_run_at_startup
                },  # in case of restart, we will start from the last bot message
                command_starters={"/start": lambda response: response.ask(ef_bot.menu)},
                commands=[
                    BotCommand(command="start", description="Start the bot"),
                    BotCommand(command="cancel", description="Cancel the current operation"),
                ],
            )

    asyncio.run(async_main())


if __name__ == "__main__":
    import typer

    typer.run(main)
