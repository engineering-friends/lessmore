from asyncio import Task
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from aiogram.types import Message
from more_itertools import first, last
from palette.teletalk.crowd.response import Response
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage
from teletalk.models.page import Page


if TYPE_CHECKING:
    from teletalk.talk import Talk


@dataclass
class Response:
    # - Raw response

    chat_id: int = 0
    callback_id: str = ""
    block_messages: list[BlockMessage] = field(default_factory=list)

    # - Pages and Blocks

    page: Optional[Page] = None  # root Block is the Block that spawned the whole conversation
    root_block: Optional[Block] = None
    block: Optional[Block] = None

    # - Talk

    talk: Optional["Talk"] = None  # circular import

    # - Navigation

    root: Optional[Response] = None
    previous: Optional[Response] = None
    next: Optional[Response] = None

    # - Syntax sugar

    async def ask(self, *args, **kwargs):
        # - Set default chat id from the response chat

        kwargs["default_chat_id"] = kwargs.pop("default_chat_id", self.chat_id)
        kwargs["parent_response"] = self

        # - Ask

        return await self.talk.ask(*args, **kwargs)

    async def tell(self, *args, **kwargs):
        # - Set default chat id from the response chat

        kwargs["default_chat_id"] = kwargs.pop("default_chat_id", self.chat_id)

        # - Tell the talk

        return await self.talk.tell(*args, **kwargs)
