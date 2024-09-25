from typing import Callable, Optional

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from teletalk.blocks.build_default_message_callback import build_default_message_callback
from teletalk.blocks.default_on_response import default_on_response
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response


go_back = lambda response: response.ask(response.previous if response.previous else response, mode="inplace")
go_forward = lambda response: response.ask(response.next if response.next else response, mode="inplace")
go_to_root = lambda response: response.ask(response.root, mode="inplace")


class SimpleBlock(Block):
    def __init__(
        self,
        text: str = "",
        keyboard: Optional[ReplyKeyboardMarkup | list[list[str]]] = None,
        one_time_keyboard: bool = True,
        inline_keyboard: Optional[InlineKeyboardMarkup | list[list[str | tuple[str, Callable]]]] = None,
        files: list[str] = [],
        message_callback: Optional[Callable | str] = "default",
        on_response: Optional[Callable] = default_on_response,
    ):
        # - Define message callback:

        if message_callback == "default":
            message_callback = build_default_message_callback(supress_messages=bool(inline_keyboard))

        # - Update block

        self.update(
            text=text,
            keyboard=keyboard,
            inline_keyboard=inline_keyboard,
            one_time_keyboard=one_time_keyboard,
            files=files,
        )

        # - Init parent response

        super().__init__(message_callback=message_callback, on_response=on_response)

    def update(
        self,
        text: str,
        keyboard: Optional[ReplyKeyboardMarkup | list[list[str]]] = None,
        one_time_keyboard: bool = False,
        inline_keyboard: Optional[InlineKeyboardMarkup | list[list[str | tuple[str, Callable]]]] = None,
        files: list[str] = [],
    ):
        self.text = text

        if isinstance(keyboard, list):
            self.reply_keyboard_markup = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=text) for text in row] for row in keyboard],
                one_time_keyboard=True,
            )
        else:
            self.reply_keyboard_markup = keyboard

        self.one_time_keyboard = one_time_keyboard

        def _unfold(value):
            if isinstance(value, str):
                return value, None
            elif isinstance(value, (list, tuple)):
                return value[0], value[1]
            else:
                raise Exception(f"Unknown value type: {type(value)}")

        if isinstance(inline_keyboard, list):
            self.inline_keyboard_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton.model_construct(  # pydantic, but without validation
                            text=_unfold(value)[0],
                            callback_data=_unfold(value)[1]
                            if isinstance(_unfold(value)[1], Callable)
                            else None,  # put callback right in the callback_data
                            url=_unfold(value)[1]
                            if isinstance(_unfold(value)[1], str)
                            else None,  # put callback right in the callback_data
                        )
                        for value in row
                    ]
                    for row in inline_keyboard
                ]
            )
        else:
            self.inline_keyboard_markup = inline_keyboard

        self.files = files

        return self

    def output(self) -> BlockMessage:
        # - Button callback

        def build_button_callback(text: str):
            async def _button_callback(response: Response):
                assert isinstance(response.prompt_sub_block, SimpleBlock), "Block is not SimpleBlock"
                return text

            return _button_callback

        # - Return

        return BlockMessage(
            text=self.text,
            files=self.files,
            reply_keyboard_markup=ReplyKeyboardRemove()
            if isinstance(self.reply_keyboard_markup, ReplyKeyboardRemove)
            else ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=button.text,
                            callback_data=build_button_callback(text=button.text),
                        )
                        for button in row
                    ]
                    for row in self.reply_keyboard_markup.keyboard
                ],
                one_time_keyboard=self.one_time_keyboard,
            )
            if self.reply_keyboard_markup
            else None,
            inline_keyboard_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=button.text,
                            callback_data=self.register_callback(
                                build_button_callback(text=button.text)
                                if button.callback_data is None
                                else button.callback_data,
                                callback_text=button.text,
                            ),
                            url=button.url,
                        )
                        for button in row
                    ]
                    for row in self.inline_keyboard_markup.inline_keyboard
                ]
            )
            if self.inline_keyboard_markup
            else None,
        )
