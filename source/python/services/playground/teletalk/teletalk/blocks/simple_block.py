from typing import Callable, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.helpers import escape_markdown
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response


class SimpleBlock(Block):
    def __init__(
        self,
        text: str = "",
        reply_keyboard_markup: Optional[ReplyKeyboardMarkup | list[list[str]]] = None,
        inline_keyboard_markup: Optional[InlineKeyboardMarkup | list[list[str | tuple[str, Callable]]]] = None,
        files: list[str] = [],
        message_callback: Optional[Callable] = lambda response: "".join(
            [message.text for message in response.block_messages]
        ),
    ):
        self.update(
            text=text,
            reply_keyboard_markup=reply_keyboard_markup,
            inline_keyboard_markup=inline_keyboard_markup,
            files=files,
        )
        super().__init__(message_callback=message_callback)

    def update(
        self,
        text: str,
        reply_keyboard_markup: Optional[ReplyKeyboardMarkup | list[list[str]]] = None,
        inline_keyboard_markup: Optional[InlineKeyboardMarkup | list[list[str | tuple[str, Callable]]]] = None,
        files: list[str] = [],
    ):
        self.text = text

        if isinstance(reply_keyboard_markup, list):
            self.reply_keyboard_markup = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=text) for text in row] for row in reply_keyboard_markup],
                one_time_keyboard=True,
            )
        else:
            self.reply_keyboard_markup = reply_keyboard_markup

        def _unfold(value):
            if isinstance(value, str):
                return value, None
            elif isinstance(value, (list, tuple)):
                return value[0], value[1]
            else:
                raise Exception(f"Unknown value type: {type(value)}")

        if isinstance(inline_keyboard_markup, list):
            self.inline_keyboard_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton.model_construct(
                            text=_unfold(value)[0],
                            callback_data=_unfold(value)[1],  # put callback right in the callback_data
                        )
                        for value in row
                    ]
                    for row in inline_keyboard_markup
                ]
            )
        else:
            self.inline_keyboard_markup = inline_keyboard_markup

        self.files = files

        return self

    def output(self) -> BlockMessage:
        # - Wrap inline_keyboard_markup callback_data with basic callback

        def button_callback(text: str):
            async def _button_callback(response: Response):
                assert isinstance(response.prompt_sub_block, SimpleBlock), "Block is not SimpleBlock"
                return text

            return _button_callback

        if self.inline_keyboard_markup:
            self.inline_keyboard_markup.inline_keyboard = [
                [
                    InlineKeyboardButton(
                        text=button.text,
                        callback_data=self.register_callback(
                            button_callback(text=button.text) if button.callback_data is None else button.callback_data
                        ),
                        url=button.url,
                    )
                    for button in row
                ]
                for row in self.inline_keyboard_markup.inline_keyboard
            ]

        if self.reply_keyboard_markup:
            self.reply_keyboard_markup = ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=button.text, callback_data=self.register_callback(button_callback(text=button.text))
                        )
                        for button in row
                    ]
                    for row in self.reply_keyboard_markup.keyboard
                ],
                one_time_keyboard=True,
            )

        # - Return

        return BlockMessage(
            text=escape_markdown(self.text, version=2),
            reply_keyboard_markup=self.reply_keyboard_markup,
            inline_keyboard_markup=self.inline_keyboard_markup,
            files=self.files,
        )
