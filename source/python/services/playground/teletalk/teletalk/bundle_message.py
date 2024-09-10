from dataclasses import dataclass, field
from typing import Callable

from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup


@dataclass
class BundleMessage:
    """Bundle is a collection of messages grouped together in telegram (like album)"""

    text: str
    reply_keyboard_markup: ReplyKeyboardMarkup  # menu
    inline_keyboard_markup: InlineKeyboardMarkup
    files: list[str]
    message_callback: Callable  # def message_callback(response: Response) -> None
    on_query_reply: Callable  # what to do with the messages after the query reply, def on_query_reply(messages: list[Message]) -> None

    _messages: list[Message] = field(default_factory=list)  # aiogram messages
