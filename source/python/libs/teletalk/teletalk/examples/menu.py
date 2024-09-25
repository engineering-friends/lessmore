import asyncio

from functools import partial
from typing import Callable, Optional, Tuple

from teletalk.app import App
from teletalk.blocks.simple_block import SimpleBlock, go_back, go_forward, go_to_root
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


def level_3(response: Response):
    return response.ask(
        "Level 3",
        inline_keyboard=[
            [
                ("Main menu", go_to_root),
                ("Back", go_back),
                ("Forward", go_forward),
                ("Cancel", lambda response: response.tell("Cancelled")),
            ]
        ],
    )


def level_2(response: Response):
    return response.ask(
        "Level 2",
        inline_keyboard=[
            [
                ("Level 3", level_3),
            ],
            [
                ("Main menu", go_to_root),
                ("Back", go_back),
                ("Forward", go_forward),
                ("Cancel", lambda response: response.tell("Cancelled")),
            ],
        ],
    )


def level_1(response: Response):
    return response.ask(
        "Level 1",
        inline_keyboard=[
            [
                ("Level 2", level_2),
            ],
            [
                ("Main menu", go_to_root),
                ("Back", go_back),
                ("Forward", go_forward),
                ("Cancel", lambda response: response.tell("Cancelled")),
            ],
        ],
    )


def test():
    deps = TestDeps.load()
    asyncio.run(
        App().start_polling(
            bot=deps.config.telegram_bot_token,
            initial_starters={deps.config.telegram_test_chat_id: level_1},
            message_starter=level_1,
        )
    )


if __name__ == "__main__":
    test()
