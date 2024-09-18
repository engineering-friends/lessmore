import uuid

from functools import wraps
from typing import Any, Callable, List, Optional, Tuple

from lessmore.utils.asynchronous.asyncify import asyncify
from teletalk.models.block_message import BlockMessage


class Block:
    """A collection of messages grouped together in telegram (like album)"""

    def __init__(self, message_callback: Optional[Callable] = None):
        # - State

        self.message_callback: Optional[Callable] = asyncify(message_callback) if message_callback else None
        self.query_callbacks: dict[str, Callable] = {}
        self.current_output: Optional[BlockMessage] = None  # will be updated by the `render` method

        # - Tree

        self.parent: Optional["Block"] = None
        self.children: list["Block"] = []

        # - Id

        self.id = str(uuid.uuid4())
        self.rendered_id = self.id

    def refresh_id(self):
        self.id = str(uuid.uuid4())

    def register_callback(self, callback: Callable) -> str:
        _id = str(uuid.uuid4())
        self.query_callbacks[_id] = asyncify(callback)
        return _id

    @property
    def chat_id(self) -> int:
        if not self.current_output or not self.current_output.messages:
            return 0

        return self.current_output.messages[0].chat.id

    def render(self, inherit_messages: bool = False) -> BlockMessage:
        output = self.output()
        if inherit_messages and self.current_output:
            output.messages = self.current_output.messages
        self.current_output = output
        self.rendered_id = self.id
        return output

    def output(self) -> BlockMessage:
        raise NotImplementedError

    def iter_nodes(self):  # node, parent
        yield self, self

        for child in self.children:
            for node, parent in child.iter_nodes():
                yield node, self
