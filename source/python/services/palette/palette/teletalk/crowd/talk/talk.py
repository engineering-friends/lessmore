import asyncio
import uuid

from asyncio import Task
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from aiogram.types import Message
from loguru import logger

from palette.teletalk.crowd.response import Response
from palette.teletalk.crowd.talk.callback_info import CallbackInfo
from palette.teletalk.query.query import Query


if TYPE_CHECKING:
    from palette.teletalk.crowd.chat import Chat


@dataclass
class Talk:
    # - Basic state

    chat: "Chat"  # parent import
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

    async def wait_for_response(self) -> Response:
        # - Wait for the question event

        result = await self.question_event

        # - Reset the future

        self.question_event = asyncio.get_running_loop().create_future()

        # - Return the result

        return result

    async def respond(self, response: Response, on_early_response: Optional[Callable] = None):
        # - Check if bot is thinking

        if self.is_bot_thinking:
            # - Process early messages

            if on_early_response:
                return await on_early_response(response)

            # - Do nothing otherwise

            logger.debug("Bot is thinking, ignoring event", event=response)

            return

        if self.question_event.done():
            logger.error("Question event is already done", event=response)
            return

        self.question_event.set_result(response)

    async def ask(
        self,
        query: Optional[Query] = None,
        message_callback: Optional[Callable] = None,
        inplace: bool = True,
    ):
        # - Set message callback

        message_callback = message_callback or query.message_callback

        # - Update question with query if provided

        if query:
            # - Render message (and register callbacks alongside of this process with talk.register_callback)

            rendered_message = query.render(talk=self)

            # - Render query and edit message (and register callbacks alongside of this process with talk.register_callback)

            if inplace and self.question_message:
                message = await self.question_message.edit_text(**rendered_message.to_dict())
            else:
                message = await self.starter_message.answer(**rendered_message.to_dict())

            # - Update pending question message

            self.set_question_message(message)

        # - Set thinking to false

        self.set_bot_thinking(False)

        # - Wait for talk and get callback_info

        while True:
            # - Get response

            response = await self.wait_for_response()

            # - Start thinking

            self.set_bot_thinking(True)

            if response.callback_id:
                # UI event

                if response.callback_id not in self.question_callbacks:
                    logger.error("Callback not found", callback_id=response.callback_id)
                    continue

                callback_info = self.question_callbacks[response.callback_id]

                return await callback_info.callback(
                    response=Response(
                        **{k: v for k, v in response.__dict__.items() if v},
                        talk=self,
                        root_query=query,
                        query=callback_info.query,
                    )
                )
            else:
                # Message event

                if not message_callback:
                    logger.debug("Message callback not found, skipping")
                    continue

                return await message_callback(
                    Response(
                        **{k: v for k, v in response.__dict__.items() if v},
                        talk=self,
                        root_query=query,
                        query=query,
                    )
                )
