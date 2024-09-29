import uuid

from typing import Any, Callable, List, Optional, Tuple

from lessmore.utils.asynchronous.asyncify import asyncify
from teletalk.models.block_message import BlockMessage
from teletalk.models.callback_info import CallbackInfo
from teletalk.utils.generate_id import generate_id


class BaseBlock:
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
        self.query_callback_infos: dict[str, CallbackInfo] = {}
        self.on_response: Optional[Callable] = (
            asyncify(on_response) if on_response else None
        )  # called after the response has been received

        # - Id

        self.id = generate_id()
        self.previous_id = None  # in case of refresh
        self.has_refreshed_id = None

        # - Visibility

        self.is_inline_keyboard_visible: Optional[bool] = None

        # - Output

        self.current_output: Optional[BlockMessage] = None  # will be updated by the `render` method
        self.previous_output: Optional[BlockMessage] = None

        # - Tree

        self.parent: Optional["BaseBlock"] = None
        self.children: list["BaseBlock"] = []

    def register_callback(self, callback: Callable, callback_text: str = "") -> str:
        _id = generate_id()
        self.query_callback_infos[_id] = CallbackInfo(
            callback=asyncify(callback),
            callback_id=_id,
            callback_text=callback_text,
        )
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
        self.id = generate_id()

        # - Update `is_refreshed`

        self.has_refreshed_id = True

    def render(self, inherit_messages: bool = False, transient: bool = False) -> BlockMessage:
        # - Update output

        output = self.output()
        if inherit_messages and self.current_output:
            output.messages = self.current_output.messages

        if not transient:
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
