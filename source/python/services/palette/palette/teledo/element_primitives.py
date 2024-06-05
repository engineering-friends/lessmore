import asyncio
import uuid

from abc import ABC, abstractmethod
from asyncio import Future
from dataclasses import dataclass
from typing import Callable, Optional

from aiogram.types import InlineKeyboardMarkup, Message
from palette.teledo.context import Context


@dataclass
class RenderedElement:
    text: str = ""
    reply_markup: Optional[InlineKeyboardMarkup] = None


class Element(ABC):
    @abstractmethod
    def render(self, context: Context) -> RenderedElement:
        pass
