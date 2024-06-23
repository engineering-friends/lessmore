import asyncio
import uuid

from dataclasses import dataclass, field
from typing import Callable, Optional

from aiogram.types import Message

from palette.teletalk.context import Question
from palette.teletalk.context.callback_info import CallbackInfo
from palette.teletalk.elements.element import Element


@dataclass
class Talk:
    user_id: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: dict = field(default_factory=dict)
    question: Question = field(default_factory=Question)
    sample_message: Optional[Message] = None  # used for answering to the user with in the same chat

    # - Question

    message: Optional[Message] = None
    ui_callbacks: dict[str, CallbackInfo] = field(default_factory=dict)
    message_callback: Optional[CallbackInfo] = None

    # will be set with CallbackEvent from global handler (callback_query/message)
    callback_future: Optional[asyncio.Future] = field(
        default_factory=lambda: asyncio.get_running_loop().create_future()
    )

    def register_ui_callback(
        self,
        callback: Callable,
        element: Element,
    ):
        _id = str(uuid.uuid4())
        self.ui_callbacks[_id] = CallbackInfo(callback=callback, element=element)
        return _id

    def register_message_callback(self, callback: Callable):
        self.message_callback = CallbackInfo(callback=callback, element=None)
