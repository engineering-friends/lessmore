from typing import Callable

from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.teletalk.crowd.talk import Talk
from palette.teletalk.elements.element import Element
from palette.teletalk.elements.rendered_element import RenderedElement


class ButtonElement(Element):
    def __init__(self, text: str, callback: Callable, message_callback: Callable = None):
        self.text = text
        self.callback = callback
        self.message_callback = message_callback

    def render(self, talk: Talk) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=self.text,
            callback_data=talk.register_question_callback(
                callback=self.callback,
                element=self,
            ),
        )
        return RenderedElement(text="Button text", reply_markup=keyboard.as_markup())