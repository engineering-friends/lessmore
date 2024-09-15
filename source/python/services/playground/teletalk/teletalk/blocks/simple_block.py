from typing import Callable, Optional

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from teletalk.models.block import Block, persist
from teletalk.models.block_message import BlockMessage


class SimpleBlock(Block):
    def __init__(
        self,
        text: str = "",
        reply_keyboard_markup: Optional[ReplyKeyboardMarkup] = None,
        inline_keyboard_markup: Optional[InlineKeyboardMarkup] = None,
        files: list[str] = [],
        message_callback: Optional[Callable] = lambda response: "".join(
            [message.text for message in response.block_messages]
        ),
    ):
        self.text = text
        self.reply_keyboard_markup = reply_keyboard_markup
        self.inline_keyboard_markup = inline_keyboard_markup
        self.files = files

        super().__init__(message_callback=message_callback)

    @persist
    def render(self) -> BlockMessage:
        return BlockMessage(
            text=self.text,
            reply_keyboard_markup=self.reply_keyboard_markup,
            inline_keyboard_markup=self.inline_keyboard_markup,
            files=self.files,
        )
