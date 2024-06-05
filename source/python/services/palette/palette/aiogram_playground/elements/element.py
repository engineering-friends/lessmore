from dataclasses import dataclass
from typing import Optional

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.aiogram_playground.elements.merge_keyboards import test


callbacks = {}


@dataclass
class RenderedElement:
    text: str = ""
    reply_markup: Optional[InlineKeyboardMarkup] = None


class EmptyElement:
    def render(self) -> RenderedElement:
        return RenderedElement()


class ButtonElement:
    def __init__(self, text: str):
        self.text = text

    def render(self) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()

        def _button_callback():
            self.message = "Button clicked"
            return self.render()

        callbacks["button"] = _button_callback
        keyboard.button(text=self.text, callback_data="button")
        return RenderedElement(text="", reply_markup=keyboard.as_markup())


if __name__ == "__main__":
    test()
