import asyncio
import uuid

from dataclasses import dataclass, field
from typing import Callable, Optional

from aiogram.types import Message


@dataclass
class CallbackEvent:
    type: str  # "ui" or "message"
    callback_id: str = ""
    message: Optional[Message] = None


@dataclass
class Question:
    message: Message
    ui_callbacks: dict[str, Callable] = field(default_factory=dict)
    message_callback: Optional[Callable] = None

    callback_future: Optional[asyncio.Future] = field(
        default_factory=lambda: asyncio.get_running_loop().create_future()
    )  # will be set with CallbackEvent from global handler (callback_query/message)


@dataclass
class Interaction:
    user_id: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: dict = field(default_factory=dict)
    pending_question: Optional[Question] = None
