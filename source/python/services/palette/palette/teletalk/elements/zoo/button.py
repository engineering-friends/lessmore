from typing import Callable, Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.teletalk.crowd.talk import Talk
from palette.teletalk.elements.element import Element
from palette.teletalk.elements.rendered_element import RenderedElement


class Button(Element):
    def __init__(self, text: str, callback: Callable):
        self.text = text
        self.callback = callback

    def render(self, talk: Talk) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=self.text,
            callback_data=talk.register_question_callback(
                callback=self.callback,
                element=self,
            ),
        )
        return RenderedElement(
            text="Button text",
            reply_markup=keyboard.as_markup(),
        )
