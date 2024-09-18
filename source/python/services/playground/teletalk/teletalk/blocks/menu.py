from typing import Callable, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage


go_back = lambda response: response.ask(response.previous if response.previous else response, update_mode="inplace")
go_forward = lambda response: response.ask(response.next if response.next else response, update_mode="inplace")
go_to_root = lambda response: response.ask(response.root, update_mode="inplace")


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
