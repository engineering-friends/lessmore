from typing import Callable

from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.teletalk.context.interaction import Interaction
from palette.teletalk.elements.element import Element
from palette.teletalk.elements.rendered_element import RenderedElement


class ButtonElement(Element):
    def __init__(self, text: str, callback: Callable, message_callback: Callable = None):
        self.text = text
        self.callback = callback
        self.message_callback = message_callback

    def render(self, interaction: Interaction) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=self.text,
            callback_data=interaction.question.register_ui_callback(
                callback=self.callback,
                element=self,
            ),
        )
        interaction.question.register_message_callback(callback=self.message_callback)
        return RenderedElement(text="Button text", reply_markup=keyboard.as_markup())
