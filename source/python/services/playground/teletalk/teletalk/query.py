import uuid

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple

from aiogram.types import InlineKeyboardMarkup


@dataclass
class QuestionMessage:
    text: str = ""
    reply_markup: Optional[InlineKeyboardMarkup] = None
    on_query_reply: Callable[[Any], str] = None  # Callback to handle message after query reply


@dataclass
class RenderedQuery:
    questions: dict[str, list[QuestionMessage]] = field(default_factory=dict)  # by chat_id
    menus: dict[str, InlineKeyboardMarkup] = field(default_factory=dict)  # by chat_id
    message_callbacks: dict[str, Callable] = field(default_factory=dict)  # by chat_id


class Query:
    def __init__(self):
        self.parent: Optional["Query"] = None
        self.children: list["Query"] = []

    def render(self, callback_wrapper: Callable) -> RenderedQuery:
        pass
