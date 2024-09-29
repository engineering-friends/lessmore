from typing import Callable, Literal, Optional

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from pymaybe import maybe
from teletalk.blocks.build_default_message_callback import build_default_message_callback
from teletalk.blocks.default_on_response import default_on_response
from teletalk.models.base_block import BaseBlock
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response


go_back = lambda response: response.ask(response.previous if response.previous else response, mode="inplace")
go_forward = lambda response: response.ask(response.next if response.next else response, mode="inplace")
go_to_root = lambda response: response.ask(response.root, mode="inplace")


class Block(BaseBlock):
    def __init__(
        self,
        text: str = "",
        keyboard: Optional[ReplyKeyboardMarkup | list[list[str]]] = None,
        one_time_keyboard: bool = True,
        inline_keyboard: Optional[InlineKeyboardMarkup | list[list[str | tuple[str, Callable]]]] = None,
        files: list[str] = [],
        message_callback: Optional[Callable | Literal["default", "raw"]] = "default",
        on_response: Optional[Callable] = default_on_response,
    ):
        # - Define message callback:

        if message_callback == "default":
            message_callback = build_default_message_callback(supress_messages=bool(inline_keyboard))
        elif message_callback == "raw":
            message_callback = lambda response: response.message

        # - Update block

        self.text = ""
        self.reply_keyboard_markup = None
        self.inline_keyboard_markup = None
        self.one_time_keyboard = False
        self.files = []

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
        text: str = ...,
        keyboard: Optional[ReplyKeyboardMarkup | list[list[str]]] = ...,
        one_time_keyboard: bool = ...,
        inline_keyboard: Optional[InlineKeyboardMarkup | list[list[str | tuple[str, Callable]]]] = ...,
        files: list[str] = ...,
    ):
        self.text = text if text is not ... else self.text

        if keyboard is not ...:
            if isinstance(keyboard, list):
                # simple list of strings to keyboard

                self.reply_keyboard_markup = ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text=text) for text in row] for row in keyboard],
                    one_time_keyboard=one_time_keyboard,
                )
            else:
                # pass as is

                self.reply_keyboard_markup = keyboard

        if inline_keyboard is not ...:

            def _pairify(value):
                if isinstance(value, str):
                    return value, None
                elif isinstance(value, (list, tuple)):
                    return value[0], value[1]
                else:
                    raise Exception(f"Unknown value type: {type(value)}")

            if isinstance(inline_keyboard, list):
                # simple list of strings to inline keyboard

                self.inline_keyboard_markup = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton.model_construct(  # pydantic, but without validation
                                text=_pairify(value)[0],
                                callback_data=_pairify(value)[1]
                                if isinstance(_pairify(value)[1], Callable)
                                else None,  # put callback right in the callback_data
                                url=_pairify(value)[1]
                                if isinstance(_pairify(value)[1], str)
                                else None,  # put callback right in the callback_data
                            )
                            for value in row
                        ]
                        for row in inline_keyboard
                    ]
                )
            else:
                # pass as is
                self.inline_keyboard_markup = inline_keyboard

        if one_time_keyboard is not ...:
            self.one_time_keyboard = one_time_keyboard

        if files is not ...:
            self.files = files

        return self

    def output(self) -> BlockMessage:
        # - Button callback

        def build_button_callback(text: str):
            async def _button_callback(response: Response):
                assert isinstance(response.prompt_sub_block, Block), "Block is not SimpleBlock"
                return text

            return _button_callback

        # - Register simple callbacks for each button

        for row in maybe(self.inline_keyboard_markup).inline_keyboard.or_else([]):
            for button in row:
                button.callback_data = (
                    button.callback_data
                    if isinstance(button.callback_data, str)
                    else (
                        self.register_callback(
                            button.callback_data
                            if isinstance(button.callback_data, Callable)
                            else build_button_callback(button.text),
                            callback_text=button.text,
                        )
                    )
                )

        # - Return

        return BlockMessage(
            text=self.text,
            files=self.files,
            reply_keyboard_markup=self.reply_keyboard_markup,
            inline_keyboard_markup=self.inline_keyboard_markup,
        )
