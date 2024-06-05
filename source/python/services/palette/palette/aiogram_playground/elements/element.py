from dataclasses import dataclass
from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder


@dataclass
class RenderedElement:
    message: str = ""
    keyboard_markup: Optional[InlineKeyboardBuilder] = None


class EmptyElement:
    def render(self) -> RenderedElement:
        return RenderedElement()


def merge_keyboards(keyboards):
    merged_keyboard = InlineKeyboardBuilder()
    for keyboard in keyboards:
        for row in keyboard.as_markup().inline_keyboard:
            for button in row:
                merged_keyboard.button(text=button.text, callback_data=button.callback_data)
    return merged_keyboard


def test():
    # Define two keyboards
    keyboard1 = InlineKeyboardBuilder()
    keyboard1.button(text="Go to Level 1", callback_data="go_to_level_1")

    keyboard2 = InlineKeyboardBuilder()
    keyboard2.button(text="Go to Level 2", callback_data="go_to_level_2")

    merged_keyboard = merge_keyboards(keyboards=[keyboard1, keyboard2])

    # Use the merged keyboard
    print(merged_keyboard.as_markup())


if __name__ == "__main__":
    test()
