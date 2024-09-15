from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from teletalk.models.block import Block, persist
from teletalk.models.block_message import BlockMessage


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

#
# @dataclass
# class Button(Block):
#     text: str
#     callback: Callable


class InlineKeyboard(Block):
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


back = Button(text="Back", callback=lambda response: response.ask(response.previous))
cancel = Button(text="Cancel", callback=lambda response: response.ask(response.root))
quit = Button(text="Quit", callback=lambda response: print("Quitting..."))


starter = lambda response: response.ask(
    Menu(
        [
            Button(
                text="A",
                callback=lambda response: response.ask(
                    page=Menu(
                        buttons=[
                            Button(
                                text="A.1", callback=lambda response: (print("A.1"), response.ask(page=response.root))
                            ),
                            Button(
                                text="A.2", callback=lambda response: (print("A.2"), response.ask(page=response.root))
                            ),
                            back,
                            cancel,
                        ]
                    ),
                    update_mode="inplace",
                ),
            ),
            Button(
                text="B",
                callback=lambda response: response.ask(
                    page=Menu(
                        buttons=[
                            Button(
                                text="B.1", callback=lambda response: (print("B.1"), response.ask(page=response.root))
                            ),
                            Button(
                                text="B.2", callback=lambda response: (print("B.2"), response.ask(page=response.root))
                            ),
                            back,
                            cancel,
                        ]
                    ),
                    update_mode="inplace",
                ),
            ),
            quit,
        ]
    )
)
