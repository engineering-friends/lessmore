from typing import Callable

from aiogram.types import CallbackQuery, Message
from teletalk.models.response import Response


class Dispatcher:
    def __init__(
        self,
        message_starter: Callable,
        command_starters: dict[str, Callable] = {},
    ):
        """Dispatcher receives the `Response` from the user and dispatches it to the appropriate `Talk`.
        - receives the `Response`
        - collects the messages in a buffer
        - when the buffer is full, builds the response and sends it to the appropriate `Talk` or creates a new `Talk`"""

        # - Args

        self.message_starter = message_starter
        self.command_starters = command_starters

        # - State

        self.message_buffers_by_chat_id: dict[int, list[Message]] = {}

    def __call__(self, response: Response) -> None:
        # - Find the `Talk` by message_id

        # - If callback_query

        # -- If didn't find the `Talk`: skip it

        # -- If found: send the event to the `Talk`

        # - If messages

        # -- Add messages to the buffer

        # -- If buffer is full: close the buffer and build the `Response` with the buffer

        # --- If a command - start a new `Talk` with the command starter

        # --- If not a command and the `Talk` is found: send the event to the `Talk`

        # --- If not a command and the `Talk` is not found: start a new `Talk` with the message starter

        pass
