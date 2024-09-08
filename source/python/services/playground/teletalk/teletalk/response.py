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
    def tell(self):  # todo later: make a better solution for this [@marklidenberg]
        return self.message or self.talk.starter_message

    async def ask(self, query: Optional[Query] = None):
        return await self.talk.ask(
            query=query or self.query,
        )

    def start_new_talk(self, callback: Callable, starter_message: Optional[Message] = None) -> Task:
        return self.talk.chat.start_new_talk(
            starter_message=starter_message or self.talk.starter_message,
            starter=callback,
        )
