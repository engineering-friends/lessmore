import asyncio
import uuid

from dataclasses import dataclass, field
from typing import Callable, Optional

from aiogram.types import Message

from palette.teletalk.crowd.callback_info import CallbackInfo
from palette.teletalk.elements.element import Element


@dataclass
class Talk:
    starter_message: Optional[Message] = None
    question_message: Optional[Message] = None
    question_callbacks: dict[str, CallbackInfo] = field(default_factory=dict)

    # will be set with CallbackEvent from global handler (callback_query/message)
    question_event: Optional[asyncio.Future] = field(default_factory=lambda: asyncio.get_running_loop().create_future())

    def register_question_callback(
        self,
        callback: Callable,
        element: Element,
    ):
        _id = str(uuid.uuid4())
        self.question_callbacks[_id] = CallbackInfo(callback=callback, element=element)
        return _id
