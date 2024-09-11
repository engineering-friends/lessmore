from typing import Callable

from aiogram.types import CallbackQuery, Message
from teletalk.models.response import Response


class Dispatcher:
    def __init__(
        self,
        message_starter: Callable,
        command_starters: dict[str, Callable] = {},
    ):
        # - Args

        self.message_starter = message_starter
        self.command_starters = command_starters

        # - State

        self.message_buffers_by_chat_id: dict[int, list[Message]] = {}

    def __call__(self, response: Response) -> None:
        # - Find the talk by message_id

        # - If callback_query

        # -- If didn't find the talk: skip it

        # -- If found: send the event to the talk

        # - If messages

        # -- Add messages to the buffer

        # -- If buffer is full: close the buffer

        # --- If talk is found: send the event to the talk

        # --- If not found: start a new talk with the proper starter (message or command)

        pass
