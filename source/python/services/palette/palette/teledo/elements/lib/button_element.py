from typing import Callable

from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.aiogram_playground.element_bot import RenderedElement
from palette.teledo.elements.element import Element
from palette.teledo.register_callback import register_callback


class ButtonElement(Element):
    def __init__(self, text: str, callback: Callable):
        self.text = text
        self.callback = callback  # will receive callback_query

    def render(self) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=self.text,
            callback_data=register_callback(element=self, callback=self.callback),
        )
        return RenderedElement(text="Button text", reply_markup=keyboard.as_markup())
