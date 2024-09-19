import asyncio

from aiogram.types import BotCommand
from ef_bots.ef_org_bot.add_user_to_chats import add_user_to_chats
from ef_bots.ef_org_bot.deps.deps import Deps
from loguru import logger
from teletalk.app import App
from teletalk.blocks.simple_block import SimpleBlock, default_message_callback
from teletalk.models.response import Response
from telethon.tl.types import User


class CancelError(Exception):
    pass


def cancel_callback(supress_messages: bool = False):
    async def _cancel_callback(response: Response):
        if response.block_messages[-1].text == "/cancel":
            raise CancelError("Cancelled")
        elif response.block_messages[-1].text:
            if supress_messages:
                return await response.ask(mode="inplace")
            else:
                return default_message_callback(response)

    return _cancel_callback


def menu(deps: Deps):
    async def start_onboarding(response: Response):
        return await response.ask()

    async def safe_start_onboarding(response: Response):
        try:
            return await start_onboarding(response)
        except CancelError:
            return await response.ask()
        except Exception as e:
            logger.error("Failed to start onboarding", error=e)
            await response.tell(f"Ошибка во время процесса онбординга: {str(e)}")
            return await response.ask()

    return SimpleBlock(
        "⚙️ *Выбери действие*",
        inline_keyboard=[
            [("Заонбордить участника", safe_start_onboarding)],
            [("Notion EF Org", "https://www.notion.so/Org-48f403a0d3014dc4972f08060031308e?pvs=4")],
            [("Стратегия и задачи", "https://www.notion.so/f3f7637c9a1d4733a4d90b33796cf78e?pvs=4")],
            [("Тексты кандидатам", "https://www.notion.so/EF-f1c2d3aeceb04272a61beb6c08c92b47?pvs=4")],
        ],
        message_callback=lambda response: response.ask(mode="inplace"),
    )


def main(env="test"):
    async def _main():
        # - Init deps

        deps = Deps.load(env=env)

        # - Start user

        await deps.telegram_user_client.start()

        # # - Start bot

        await App(
            bot=deps.config.telegram_bot_token,
            command_starters={"/start": lambda response: response.ask(menu(deps))},
            commands=[
                BotCommand(command="start", description="Start the bot"),
                BotCommand(command="cancel", description="Cancel the current operation"),
            ],
        ).start_polling()

    asyncio.run(_main())


if __name__ == "__main__":
    import fire

    fire.Fire(main)
