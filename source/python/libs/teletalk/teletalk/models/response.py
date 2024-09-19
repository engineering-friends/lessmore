from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from lessmore.utils.functional.dict.drop import drop
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

    root: Optional["Response"] = None  # always triggered by a text message, a starter
    previous: Optional["Response"] = None
    next: Optional["Response"] = None

    # - Syntax sugar

    async def ask(self, *args, **kwargs):
        # - Set default args as the response itself

        if not args and not drop(kwargs, keys=["mode"]):
            args = (self,)  # <=> response.ask(response)

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

    async def purge_talk(self):
        return await self.talk.purge()

    async def purge(self):
        # delete all messages from the current response
        for block_message in self.block_messages:
            for message in block_message.messages:
                await self.talk.upsert_message(old_message=message)

    def response_stack(self):
        result = []
        current_response = self.root
        while current_response:
            result.append(current_response)
            current_response = current_response.next
        return result

    async def start_new_talk(self, *args, **kwargs):
        return await self.talk.start_new_talk(*args, **kwargs)
