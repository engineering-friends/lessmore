from dataclasses import dataclass
from typing import Optional

from aiogram.types import InlineKeyboardMarkup


@dataclass
class RenderedElement:
    text: str = ""
    reply_markup: Optional[InlineKeyboardMarkup] = None