import asyncio

from typing import Callable, Optional, Tuple

from teletalk.app import App
from teletalk.blocks.menu import Menu, go_back, go_forward, go_to_root
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


def gen_level(name: str, sub_level: Optional[Menu] = None):
    # - Build grid

    grid = []

    if sub_level:
        grid.append([(sub_level.text, lambda response: response.ask(sub_level, update_mode="inplace"))])

    grid += [
        [
            ("Main menu", go_to_root),
            ("Back", go_back),
            ("Forward", go_forward),
            ("Cancel", lambda response: response.tell("Cancelled")),
        ]
    ]

    # - Return menu

    return Menu(text=name, grid=grid)


level_3 = gen_level("Level 3")
level_2 = gen_level("Level 2", level_3)
level_1 = gen_level("Level 1", level_2)


async def starter(response: Response):
    return await response.ask(level_1)


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            command_starters={"/start": starter},
        ).start_polling()
    )


if __name__ == "__main__":
    test()
