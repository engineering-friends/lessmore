from asyncio import Task
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from aiogram.types import Message


@dataclass
class RawResponse:
    callback_id: str = ""
    messages: Optional[Message] = None
