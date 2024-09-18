import asyncio

from typing import Callable, Optional, Tuple

from teletalk.app import App
from teletalk.blocks.menu import Menu, go_back, go_forward, go_to_root
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def start_onboarding(response: Response):
    # - Ask for name

    name = await response.ask("Как зовут?")

    # - Ask for telegram username

    telegram_username = await response.ask("Ник в телеге")

    # - Add to all telegram ecosystem: ef channel, ef random coffee

    # - Create notion page for the user, if not exists


main_menu = Menu(
    "Выбери действие:",
    grid=[("Заонбордить участника", start_onboarding)],
)


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            command_starters={"/start": lambda response: response.ask(main_menu)},
        ).start_polling()
    )


if __name__ == "__main__":
    test()
