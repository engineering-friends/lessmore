import uuid

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from teletalk.bundle_message import BundleMessage


@dataclass
class RenderedQuery:
    bundles_by_chat_id: dict[str, list[BundleMessage]] = field(default_factory=dict)
    global_menus: dict[str, ReplyKeyboardMarkup] = field(default_factory=dict)
    global_message_callbacks: dict[str, Callable] = field(default_factory=dict)

    def menus(self):
        return {
            chat_id: bundles[-1].reply_keyboard_markup for chat_id, bundles in self.bundles_by_chat_id.items()
        } | self.global_menus

    def message_callbacks(self):
        return {
            chat_id: bundles[-1].message_callback for chat_id, bundles in self.bundles_by_chat_id.items()
        } | self.global_message_callbacks


class Query:
    def __init__(self):
        self.parent: Optional["Query"] = None
        self.children: list["Query"] = []

    def render(self, callback_wrapper: Callable) -> RenderedQuery:
        pass
