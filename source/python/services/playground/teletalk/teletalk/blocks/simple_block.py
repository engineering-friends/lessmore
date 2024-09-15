from typing import Callable, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.helpers import escape_markdown
from teletalk.models.block import Block, persist
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response


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
        # - Wrap inline_keyboard_markup callback_data with basic callback

        def button_callback(text: str):
            async def _button_callback(response: Response):
                assert isinstance(response.block, SimpleBlock), "Block is not SimpleBlock"

                # - Remove inline keyboard from th message

                # await response.tell(text=response.block.text) # todo later: add this back [@marklidenberg]

                # - Return the button text

                return text

            return _button_callback

        if self.inline_keyboard_markup:
            self.inline_keyboard_markup.inline_keyboard = [
                [
                    InlineKeyboardButton(
                        text=button.text,
                        callback_data=self.register_callback(button_callback(text=button.text)),
                    )
                    for button in row
                ]
                for row in self.inline_keyboard_markup.inline_keyboard
            ]

        # - Return

        return BlockMessage(
            text=escape_markdown(self.text, version=2),
            reply_keyboard_markup=self.reply_keyboard_markup,
            inline_keyboard_markup=self.inline_keyboard_markup,
            files=self.files,
        )
