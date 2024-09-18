import asyncio

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from teletalk.app import App
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


class Menu(Block):
    def __init__(
        self,
        text: str,
        grid: list[list[Tuple[str, Optional[Callable]]]],
    ):
        self.text = text
        self.grid = grid
        super().__init__()

    def output(self) -> BlockMessage:
        return BlockMessage(
            text=self.text,
            inline_keyboard_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=text, callback_data=self.register_callback(callback))
                        for text, callback in row
                    ]
                    for row in self.grid
                ]
            ),
        )


go_back = lambda response: response.ask(response.previous, update_mode="inplace")
go_forward = lambda response: response.ask(response.next, update_mode="inplace")
go_to_root = lambda response: response.ask(response.root, update_mode="inplace")
cancel = lambda response: response.tell("Cancelled")


def gen_level(name: str, sub_level: Optional[Menu] = None):
    # - Build grid

    grid = []

    if sub_level:
        grid.append([(sub_level.text, lambda response: response.ask(sub_level, update_mode="inplace"))])

    grid += [[("Main menu", go_to_root), ("Back", go_back), ("Forward", go_forward), ("Cancel", cancel)]]

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
