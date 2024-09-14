import uuid

from typing import Any, Callable, List, Optional, Tuple

from aiogram.types import ReplyKeyboardMarkup
from teletalk.models.block_message import BlockMessage
from teletalk.models.callback_info import CallbackInfo


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

        # - State

        self.callback_infos: dict[str, CallbackInfo] = {}
        self.rendered: Optional[BlockMessage] = None

        # - Tree

        self.parent: Optional["Block"] = None
        self.children: list["Block"] = []

    def get_callback_id(self, callback: Callable) -> str:
        _id = str(uuid.uuid4())
        self.callback_infos[_id] = CallbackInfo(callback_id=_id, callback=callback)
        return _id

    def render(self) -> BlockMessage:
        raise NotImplementedError

    def render_and_cache(self):
        self.rendered = self.render()
        return self.rendered
