import asyncio

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class CallbackEvent:
    type: str  # "ui" or "message"
    callback_id: str
    data: dict


@dataclass
class Question:
    message_id: str = ""
    ui_callbacks: dict[str, Callable] = field(default_factory=dict)  # callback_id -> callback
    message_callback: Optional[Callable] = None

    _callback_future: Optional[asyncio.Future] = field(
        default_factory=lambda: asyncio.get_running_loop().create_future()
    )  # when new UI event or message event is received, we set the future that current interaction awaits for


@dataclass
class Interaction:
    id: str = ""
    user_id: str = ""
    state: dict = field(default_factory=dict)
    question: Optional[Question] = None

    @property
    def is_active(self):
        return self.ask_message_id != ""
