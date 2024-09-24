import uuid

from functools import wraps
from typing import Any, Callable, List, Optional, Tuple

from lessmore.utils.asynchronous.asyncify import asyncify
from teletalk.models.block_message import BlockMessage


class Block:
    """A collection of messages grouped together in telegram (like album)"""

    def __init__(
        self,
        message_callback: Optional[Callable] = None,
        external_callback: Optional[Callable] = None,
        on_response: Optional[Callable] = None,
    ):
        # - State

        self.message_callback: Optional[Callable] = asyncify(message_callback) if message_callback else None
        self.external_callback: Optional[Callable] = asyncify(external_callback) if external_callback else None
        self.query_callbacks: dict[str, Callable] = {}
        self.on_response: Optional[Callable] = (
            asyncify(on_response) if on_response else None
        )  # called after the response has been received

        # - Id

        self.id = str(uuid.uuid4())
        self.previous_id = None  # in case of refresh
        self.has_refreshed_id = None

        # - Visibility

        self.is_inline_keyboard_visible: Optional[bool] = None

        # - Output

        self.current_output: Optional[BlockMessage] = None  # will be updated by the `render` method
        self.previous_output: Optional[BlockMessage] = None

        # - Tree

        self.parent: Optional["Block"] = None
        self.children: list["Block"] = []

    def register_callback(self, callback: Callable) -> str:
        _id = str(uuid.uuid4())
        self.query_callbacks[_id] = asyncify(callback)
        return _id

    @property
    def chat_id(self) -> int:
        if not self.current_output or not self.current_output.messages:
            return 0

        return self.current_output.messages[0].chat.id

    def refresh_id(self):
        # - Update outputs

        self.previous_output = self.current_output
        self.current_output = None

        # - Update ids

        self.previous_id = self.id
        self.id = str(uuid.uuid4())

        # - Update `is_refreshed`

        self.has_refreshed_id = True

    def render(
        self,
        inherit_messages: bool = False,
    ) -> BlockMessage:
        # - Update output

        output = self.output()
        if inherit_messages and self.current_output:
            output.messages = self.current_output.messages

        if self.current_output:
            self.previous_output = self.current_output
        self.current_output = output

        # - Reset `is_refreshed`

        self.has_refreshed_id = None

        # - Set is_inline_keyboard_visible to the output if not set

        if self.is_inline_keyboard_visible is not None:
            output.is_inline_keyboard_visible = self.is_inline_keyboard_visible

        # - Return output

        return output

    def output(self) -> BlockMessage:
        raise NotImplementedError

    def iter_nodes(self):  # node, parent
        yield self, self

        for child in self.children:
            for node, parent in child.iter_nodes():
                yield node, self
