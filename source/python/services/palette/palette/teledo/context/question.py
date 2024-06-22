import asyncio
import uuid

from dataclasses import dataclass, field
from typing import Callable, Optional

from aiogram.types import Message

from palette.teledo.context.callback_info import CallbackInfo
from palette.teledo.elements.element import Element


@dataclass
class Question:
    message: Optional[Message] = None
    ui_callbacks: dict[str, CallbackInfo] = field(default_factory=dict)
    message_callback: Optional[CallbackInfo] = None

    callback_future: Optional[asyncio.Future] = field(
        default_factory=lambda: asyncio.get_running_loop().create_future()
    )  # will be set with CallbackEvent from global handler (callback_query/message)

    def register_ui_callback(
        self,
        callback: Callable,
        element: Element,
    ):
        _id = str(uuid.uuid4())
        self.ui_callbacks[_id] = CallbackInfo(callback=callback, element=element)
        return _id

    def register_message_callback(self, callback: Callable, element: Element):
        self.message_callback = CallbackInfo(callback=callback, element=element)
