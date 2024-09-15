from dataclasses import dataclass, field

from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup


@dataclass
class BlockMessage:
    """A collection of messages grouped together in telegram (like album)"""

    # - Args

    chat_id: str
    text: str
    reply_keyboard_markup: ReplyKeyboardMarkup
    inline_keyboard_markup: InlineKeyboardMarkup
    files: list[str]

    # - State

    messages: list[Message] = field(default_factory=list)  # aiogram messages
