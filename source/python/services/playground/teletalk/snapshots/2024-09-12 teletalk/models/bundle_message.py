from dataclasses import dataclass, field

from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup


@dataclass
class BundleMessage:
    """Bundle is a collection of messages grouped together in telegram (like album)"""

    chat_id: str
    text: str
    reply_keyboard_markup: ReplyKeyboardMarkup  # menu
    inline_keyboard_markup: InlineKeyboardMarkup
    files: list[str]

    messages: list[Message] = field(default_factory=list)  # aiogram messages
