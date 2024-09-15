import uuid

from functools import wraps
from typing import Any, Callable, List, Optional, Tuple

from aiogram.types import ReplyKeyboardMarkup
from teletalk.models.block_message import BlockMessage


class Block:
    """A collection of messages grouped together in telegram (like album)"""

    def __init__(
        self,
        chat_id: str = "",
        message_callback: Optional[Callable] = None,  # def message_callback(response: Response) -> None
    ):
        # - Args

        self.chat_id = chat_id
        self.message_callback: Optional[Callable] = message_callback

        # - State

        self.query_callbacks: dict[str, Callable] = {}
        self.rendered: Optional[BlockMessage] = None

        # - Tree

        self.parent: Optional["Block"] = None
        self.children: list["Block"] = []

    def get_callback_id(self, callback: Callable) -> str:
        _id = str(uuid.uuid4())
        self.query_callbacks[_id] = callback
        return _id

    def getattr(self, name: str) -> Any:
        # hack to cache the render method
        if name == "render":
            value = object.__getattribute__(self, name)()
            self.rendered = value
            return value
        else:
            return object.__getattribute__(self, name)

    def render(self) -> BlockMessage:
        raise NotImplementedError
