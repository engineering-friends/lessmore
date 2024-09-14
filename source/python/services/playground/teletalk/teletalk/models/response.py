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
    # - Pages and Blocks

    root_page: Optional[Page] = None  # root Block is the Block that spawned the whole conversation
    root_block: Optional[Block] = None
    block: Optional[Block] = None

    # - Block messages

    block_messages: list[BlockMessage] = field(default_factory=list)

    # - Talk

    talk: Optional["Talk"] = None  # circular import

    # - Navigation

    root: Optional[Response] = None
    previous: Optional[Response] = None
    next: Optional[Response] = None

    # - Syntax sugar

    @property
    def block_message(self) -> Optional[BlockMessage]:
        return last(self.block_messages, default=None)
