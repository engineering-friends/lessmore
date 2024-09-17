import asyncio

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from teletalk.app import App
from teletalk.models.block import Block, persist
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


"""
- A
- B
- Quit

- A.1
- A.2
- Back
- Cancel

- B.1
- B.2
- Back
- Cancel

"""


class Menu(Block):
    def __init__(
        self,
        text: str,
        grid: list[list[Tuple[str, Optional[Callable]]]],
    ):
        self.text = text
        self.grid = grid
        super().__init__()

    @persist
    def render(self) -> BlockMessage:
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


# back = Button(text="Back", callback=lambda response: response.ask(response.previous))
# cancel = Button(text="Cancel", callback=lambda response: response.ask(response.root))
# quit = Button(text="Quit", callback=lambda response: print("Quitting..."))


async def starter(response: Response):
    return await response.ask(
        Menu(
            text="Menu",
            grid=[
                [
                    ("A", lambda response: (print("A"), response.ask(response.root, update_mode="inplace_recent"))),
                ],
            ],
        )
    )


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            command_starters={"/start": starter},
        ).start_polling()
    )


if __name__ == "__main__":
    test()
