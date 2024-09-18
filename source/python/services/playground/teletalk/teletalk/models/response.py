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
    external_payload: dict = field(default_factory=dict)

    # - Talk

    talk: Optional["Talk"] = None  # circular import

    # - Pages and Blocks

    prompt_page: Optional[Page] = None
    prompt_block: Optional[Block] = None
    prompt_sub_block: Optional[Block] = None

    # - Navigation: a call stack of responses for back and forth navigation

    root: Optional[Response] = None  # always triggered by a text message, a starter
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

    def response_stack(self):
        result = []
        current_response = self
        while current_response:
            result.append(current_response)
            current_response = current_response.previous
        return result
