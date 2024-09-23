from dataclasses import dataclass, field
from typing import Optional

from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup


@dataclass
class BlockMessage:
    """A collection of messages grouped together in telegram (like album)"""

    # - Contents

    chat_id: int = 0  # can be specified in the constructor, or will be taken from the current chat
    text: str = ""
    reply_keyboard_markup: Optional[ReplyKeyboardMarkup] = None
    inline_keyboard_markup: Optional[InlineKeyboardMarkup] = None
    is_inline_keyboard_visible: bool = True
    files: list[str] = field(default_factory=list)

    # - State

    messages: list[Message] = field(default_factory=list)  # aiogram messages

    @property
    def message_count(self) -> int:
        return 1 if not self.files else len(self.files)
