from asyncio import Task
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from aiogram.types import Message

from palette.teletalk.query.query import Query


if TYPE_CHECKING:
    from palette.teletalk.crowd.talk.talk import Talk


@dataclass
class Response:
    # - Raw response

    callback_id: str = ""
    message: Optional[Message] = None
    extra_messages: list[Message] = field(default_factory=list)

    # - Enriched response

    root_query: Optional[Query] = None
    query: Optional[Query] = None
    talk: Optional["Talk"] = None  # circular import

    # - Syntax sugar

    @property
    def tell(self):  # todo later: make a better solution for this
        return self.message or self.talk.starter_message

    @property
    def question_message(self):
        return self.talk.question_message

    def start_new_talk(self, callback: Callable, starter_message: Optional[Message] = None) -> Task:
        return self.talk.chat.start_new_talk(
            starter_message=starter_message or self.talk.starter_message,
            callback=callback,
        )

    async def ask(
        self,
        query: Optional[Query] = None,
        message_callback: Optional[Callable] = None,
        inplace: bool = True,
    ):
        return await self.talk.ask(
            query=query or self.query,
            message_callback=message_callback,
            inplace=inplace,
        )
