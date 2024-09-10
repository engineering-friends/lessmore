from dataclasses import dataclass, field
from typing import Callable

from aiogram.types import ReplyKeyboardMarkup
from teletalk.models.bundle_message import BundleMessage
from teletalk.models.query import Query


@dataclass
class RenderedMultiQuery:
    chat_bundle_messages: dict[str, list[BundleMessage]] = field(default_factory=dict)
    global_chat_reply_keyboard_markups: dict[str, ReplyKeyboardMarkup] = field(default_factory=dict)

    @property
    def chat_reply_keyboard_markups(self):
        return {
            chat_id: bundles[-1].reply_keyboard_markup for chat_id, bundles in self.chat_bundle_messages.items()
        } | self.global_chat_reply_keyboard_markups


class MultiQuery:
    def __init__(self):
        self.queries: list[Query] = []

    def render(self, callback_wrapper: Callable) -> RenderedMultiQuery:
        raise NotImplementedError
