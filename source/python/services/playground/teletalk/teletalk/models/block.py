import uuid

from functools import wraps
from typing import Any, Callable, List, Optional, Tuple

from lessmore.utils.asynchronous.asyncify import asyncify
from teletalk.models.block_message import BlockMessage


def persist(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        setattr(self, f"_{func.__name__}", func(self, *args, **kwargs))
        return getattr(self, f"_{func.__name__}")

    return wrapper


class Block:
    """A collection of messages grouped together in telegram (like album)"""

    def __init__(self, message_callback: Optional[Callable] = None):
        # - State

        self.message_callback: Optional[Callable] = asyncify(message_callback) if message_callback else None
        self.query_callbacks: dict[str, Callable] = {}
        self._render: Optional[BlockMessage] = None  # will be updated by the `render` method

        # - Tree

        self.parent: Optional["Block"] = None
        self.children: list["Block"] = []

        # - Id

        self.id = str(uuid.uuid4())

    def refresh_id(self):
        self.id = str(uuid.uuid4())

    def register_callback(self, callback: Callable) -> str:
        _id = str(uuid.uuid4())
        self.query_callbacks[_id] = asyncify(callback)
        return _id

    @property
    def chat_id(self) -> int:
        if not self._render or not self._render.messages:
            return 0

        return self._render.messages[0].chat.id

    @persist
    def render(self) -> BlockMessage:
        raise NotImplementedError
