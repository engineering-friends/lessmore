import asyncio
import uuid

from dataclasses import dataclass, field
from typing import Callable, Optional

from aiogram.types import Message

from palette.teletalk.crowd.callback_event import CallbackEvent
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

    def set_question_message(self, message: Message):
        self.question_message = message

    def reset_question_message(self):
        self.question_message = None
        self.question_callbacks = {}

    async def wait_for_question_event(self) -> CallbackEvent:
        # - Wait for the question event

        result = await self.question_event

        # - Reset the future

        self.question_event = asyncio.get_running_loop().create_future()

        # - Return the result

        return result
