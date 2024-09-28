from ef_bots.ef_org_bot.main import EFOrgBot
from teletalk.app import App


def test_start_onboarding():
    async def _main():
        async with EFOrgBot() as bot:
            async with App(
                state_backend="rocksdict",
                state_config={"path": str(bot.local_files_dir / "app_state")},
            ) as app:
                # - Load chat_ids to run at startup - the ones which have last message from the bot (usually the menu message). Needed for user not to press /start if bot has been restarted, and just used the menu of the last message (beta)

                chat_ids_to_run_at_startup = [
                    chat_id
                    for chat_id, chat_private_state in app.iter_chat_states(private=True)
                    if maybe(chat_private_state)["messages"][-1]["from_user"]["is_bot"].or_else(False)
                ]

                logger.info("Chats to run at startup", chat_ids=chat_ids_to_run_at_startup)

                # - Start polling

                await app.start_polling(
                    bot=bot.config.telegram_bot_token,
                    initial_starters={
                        chat_id: lambda response: response.ask(bot.menu, mode="inplace_latest")
                        for chat_id in chat_ids_to_run_at_startup
                    },  # in case of restart, we will start from the last bot message
                    command_starters={"/start": lambda response: response.ask(bot.menu)},
                    commands=[
                        BotCommand(command="start", description="Start the bot"),
                        BotCommand(command="cancel", description="Cancel the current operation"),
                    ],
                )

    asyncio.run(_main())


if __name__ == "__main__":
    import typer

    typer.run(main)
