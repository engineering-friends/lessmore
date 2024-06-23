import asyncio
import uuid

from dataclasses import dataclass, field
from typing import Callable, Optional

from aiogram.types import Message

import palette.teletalk.crowd.talker

from palette.teletalk.crowd.callback_event import CallbackEvent
from palette.teletalk.crowd.callback_info import CallbackInfo
from palette.teletalk.elements.element import Element


@dataclass
class Talk:
    talker: palette.teletalk.crowd.talker.Talker  # ruff: ignore
    starter_message: Optional[Message] = None
    question_message: Optional[Message] = None
    question_callbacks: dict[str, CallbackInfo] = field(default_factory=dict)
    question_event: Optional[asyncio.Future] = field(
        default_factory=lambda: asyncio.get_running_loop().create_future()
    )  # will be set with CallbackEvent from global handler (callback_query/message)

    # - Internal

    _old_question_callbacks: dict[str, CallbackInfo] = field(default_factory=dict)  # used to clean up old callbacks

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
        self.question_callbacks = {
            k: v for k, v in self.question_callbacks.items() if k not in self._old_question_callbacks.keys()
        }
        self._old_question_callbacks = dict(self.question_callbacks)

    async def wait_for_question_event(self) -> CallbackEvent:
        # - Wait for the question event

        result = await self.question_event

        # - Reset the future

        self.question_event = asyncio.get_running_loop().create_future()

        # - Return the result

        return result
