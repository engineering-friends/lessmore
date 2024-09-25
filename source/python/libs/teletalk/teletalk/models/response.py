from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Literal, Optional, Union

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from lessmore.utils.functional.dict.drop import drop
from more_itertools import only
from teletalk.blocks.default_on_response import default_on_response
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage
from teletalk.models.callback_info import CallbackInfo
from teletalk.models.page import Page


if TYPE_CHECKING:
    from teletalk.talk import Talk


@dataclass
class Response:
    # - Raw response

    chat_id: int = 0
    callback_id: str = ""
    callback_info: Optional[CallbackInfo] = None
    block_messages: list[BlockMessage] = field(default_factory=list)
    external_payload: dict = field(default_factory=dict)
    starter: Optional[Callable] = None

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

    async def ask(
        self,
        prompt: Union[str, Block, Page, "Response"] = "",
        files: Optional[list[str]] = None,
        keyboard: Optional[ReplyKeyboardMarkup | ReplyKeyboardRemove | list[list[str]]] = None,
        one_time_keyboard: bool = True,
        inline_keyboard: Optional[InlineKeyboardMarkup | list[list[str | tuple[str, Callable]]]] = None,
        message_callback: Optional[Callable | str] = "default",
        mode: Literal["inplace", "inplace_latest", "create_new"] = "create_new",
        default_chat_id: int = 0,  # usually passed from the response
        parent_response: Optional["Response"] = None,
        on_response: Optional[Callable] = default_on_response,
    ):
        return await self.talk.ask(
            prompt=prompt or self,
            files=files,
            keyboard=keyboard,
            one_time_keyboard=one_time_keyboard,
            inline_keyboard=inline_keyboard,
            message_callback=message_callback,
            mode=mode,
            default_chat_id=default_chat_id or self.chat_id,
            parent_response=parent_response or self,
            on_response=on_response,
        )

    async def tell(
        self,
        prompt: Union[str, Block, Page, "Response"] = "",
        files: Optional[list[str]] = None,
        keyboard: Optional[ReplyKeyboardMarkup | ReplyKeyboardRemove | list[list[str]]] = None,
        mode: Literal["inplace", "inplace_latest", "create_new"] = "create_new",
        default_chat_id: int = 0,
    ):
        return await self.talk.tell(
            prompt=prompt,
            files=files,
            keyboard=keyboard,
            mode=mode,
            default_chat_id=default_chat_id or self.chat_id,
        )

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

    @property
    def messages(self):
        return sum([block_message.messages for block_message in self.block_messages], [])

    @property
    def message(self):
        return only(self.messages, default=None)

    async def get_chat_state(self):
        # todo later: make async state
        return self.talk.app.state.get(f"chat_{self.chat_id}", {})

    async def set_chat_state(self, state: dict):
        # todo later: make async state
        self.talk.app.state[f"chat_{self.chat_id}"] = state
