from typing import Callable, Optional

from palette.teletalk.crowd.talk import Talk
from palette.teletalk.query.query import Query
from palette.teletalk.query.rendered_query import RenderedQuery


class Text(Query):
    def __init__(self, text: str, message_callback: Callable):
        self.text = text
        self.message_callback = message_callback

    def render(self, talk: Talk) -> RenderedQuery:
        return RenderedQuery(text=self.text)
