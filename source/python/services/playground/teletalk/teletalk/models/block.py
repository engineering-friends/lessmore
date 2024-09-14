import uuid

from typing import Any, Callable, List, Optional, Tuple

from teletalk.models.block_message import BlockMessage


class Block:
    """A collection of messages grouped together in telegram (like album)"""

    def __init__(
        self,
        chat_id: str,
        message_callback: Optional[Callable] = None,  # def message_callback(response: Response) -> None
    ):
        # - Args

        self.chat_id = chat_id
        self.message_callback: Optional[Callable] = message_callback

        # - Tree

        self.parent: Optional["Block"] = None
        self.children: list["Block"] = []

    def render(self, callback_wrapper: Callable) -> BlockMessage:
        raise NotImplementedError
