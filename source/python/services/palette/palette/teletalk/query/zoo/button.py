from typing import Callable, Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.teletalk.crowd.talk import Talk
from palette.teletalk.query.query import Query
from palette.teletalk.query.rendered_query import RenderedQuery


class Button(Query):
    def __init__(self, text: str, callback: Callable):
        self.text = text
        self.callback = callback

    def render(self, talk: Talk) -> RenderedQuery:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=self.text,
            callback_data=talk.register_question_callback(
                callback=self.callback,
                query=self,
            ),
        )
        return RenderedQuery(
            text="Button text",
            reply_markup=keyboard.as_markup(),
        )
