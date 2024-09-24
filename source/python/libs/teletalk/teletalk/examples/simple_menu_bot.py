import asyncio

from aiogram.types import BotCommand
from teletalk.app import App
from teletalk.models.response import Response


async def how_old_are_you(response: Response):
    name = await response.ask("What is your name?")
    await response.tell(f"Hello, {name}!")

    button = await response.ask("Are you 18+?", inline_keyboard=[["✅ I am 18"], ["❌ I am not 18"]])

    if button == "✅ I am 18":
        await response.tell("❤️")
    else:
        await response.tell("🙈")

    return response.ask()  # go to main menu


async def main_menu(response: Response):
    await response.ask(
        "⚙️ *Выбери действие*",
        inline_keyboard=[
            [("Привет!", how_old_are_you)],
            [
                (
                    "Claude has released a new AI tool, which is awesome",
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                )
            ],
        ],
    )


async def main():
    # - Init deps

    from teletalk.test_deps.test_deps import TestDeps

    deps = TestDeps.load()

    # - Run app

    await App(
        bot=deps.config.telegram_bot_token,
        command_starters={"/start": main_menu},
        commands=[
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="cancel", description="Cancel the current operation"),
        ],
    ).start_polling()


if __name__ == "__main__":
    asyncio.run(main())
