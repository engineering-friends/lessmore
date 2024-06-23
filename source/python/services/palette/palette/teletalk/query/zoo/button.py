from typing import Callable, Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.teletalk.crowd.talk.talk import Talk
from palette.teletalk.query.query import Query
from palette.teletalk.query.rendered_query import RenderedQuery


class Button(Query):
    def __init__(
        self, label_text: str, button_text: str, callback: Callable, message_callback: Optional[Callable] = None
    ):
        self.label_text = label_text
        self.button_text = button_text
        self.callback = callback
        self.message_callback = message_callback

    def render(self, talk: Talk) -> RenderedQuery:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=self.button_text,
            callback_data=talk.register_question_callback(
                callback=self.callback,
                query=self,
            ),
        )
        return RenderedQuery(
            text=self.label_text,
            reply_markup=keyboard.as_markup(),
        )
