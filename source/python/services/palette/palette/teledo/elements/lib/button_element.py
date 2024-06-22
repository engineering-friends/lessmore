from typing import Callable

from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.teledo.context.interaction import Interaction
from palette.teledo.elements.element import Element
from palette.teledo.elements.rendered_element import RenderedElement


class ButtonElement(Element):
    def __init__(self, text: str, callback: Callable):
        self.text = text
        self.callback = callback

    def render(self, interaction: Interaction) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=self.text,
            callback_data=interaction.pending_question.register_ui_callback(
                callback=self.callback,
                element=self,
            ),
        )
        return RenderedElement(text="Button text", reply_markup=keyboard.as_markup())
