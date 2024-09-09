import asyncio
import uuid

from asyncio import Future
from typing import Any, Callable, List, Literal, Optional

from loguru import logger
from teletalk.callback_info import CallbackInfo
from teletalk.query import Query
from teletalk.question_message import QuestionMessage


class Talk:
    def __init__(
        self,
        starter: Callable,
        start_new_talk: Callable = lambda starter, starter_message: logger.info(
            "Starting new talk", starter=starter, starter_message=starter_message
        ),
    ):
        # - Args

        self.starter = starter  # Coroutine starter for the talk
        self.start_new_talk = start_new_talk

        # - State

        self.question_messages: list[QuestionMessage] = []  # List of messages related to ongoing queries
        self.question_callbacks: list[
            CallbackInfo
        ] = []  # List of callbacks related to ongoing queries for all messages

        self.menus = []  # List of menus related to ongoing queries (for different chats)
        self.history = []  # History of interactions within the talk
        self.event_channel = asyncio.get_running_loop().create_future()  # Future to manage asynchronous events

    def ask(
        self,
        query: Query,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
    ) -> Any:
        # - Render the query messages and menus, update `self.question_messages` and `self.menus`

        # - Update messages in telegram according to the `update_mode`. Add new messages to `self.question_messages and self.history`

        # - Wait for the `raw_response` event from the global callbacks

        # - Apply `on_query_reply` for each message (spawn tasks in parallel)

        # - Build `response` and run and return appropriate callback

        pass

    def register_question_callback(
        self,
        callback: Callable,
        query: Query,
    ):
        _id = str(uuid.uuid4())
        self.question_callbacks.append(CallbackInfo(callback_id=_id, callback=callback, query=query))
        return _id

    def tell(self, **kwargs) -> None:
        # - Send the messages and add them to the `self.history`

        pass
