import asyncio
import uuid

from asyncio import Task
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from aiogram.types import Message
from loguru import logger

from palette.teletalk.crowd.callback_event import CallbackEvent
from palette.teletalk.crowd.callback_info import CallbackInfo
from palette.teletalk.query.query import Query


if TYPE_CHECKING:
    from palette.teletalk.crowd.chat import Chat


@dataclass
class Talk:
    chat: "Chat"  # circular import
    starter_message: Optional[Message] = None
    is_bot_thinking: bool = False  # will be set to True when making a response to a user message

    # - Question

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
        query: Query,
    ):
        _id = str(uuid.uuid4())
        self.question_callbacks[_id] = CallbackInfo(callback=callback, query=query)
        return _id

    def set_bot_thinking(self, is_bot_thinking: bool):
        self.is_bot_thinking = is_bot_thinking

    def set_question_message(self, message: Message):
        # - Set the question message
        self.question_message = message

        # - Set new callbacks, exclude all callbacks as outdated

        self.question_callbacks = {
            k: v for k, v in self.question_callbacks.items() if k not in self._old_question_callbacks.keys()
        }

        # - Refresh snapshot of old callbacks

        self._old_question_callbacks = dict(self.question_callbacks)

    async def wait_for_question_event(self) -> CallbackEvent:
        # - Wait for the question event

        result = await self.question_event

        # - Reset the future

        self.question_event = asyncio.get_running_loop().create_future()

        # - Return the result

        return result

    def respond(self, event: CallbackEvent):
        if self.is_bot_thinking:
            logger.debug("Bot is thinking, ignoring event", event=event)
            return

        self.question_event.set_result(event)

    # - Syntax sugar

    async def ask(
        self,
        query: Query,
        inplace: bool = True,
    ):
        return await self.chat.ask(talk=self, query=query, inplace=inplace)

    @property
    def message(self):  # for quick communication
        return self.starter_message

    def start_new_talk(self, callback: Callable, starter_message: Optional[Message] = None) -> Task:
        return self.chat.start_new_talk(
            starter_message=starter_message or self.starter_message,
            callback=callback,
        )
