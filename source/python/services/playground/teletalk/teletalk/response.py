from asyncio import Task
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from aiogram.types import Message
from more_itertools import first, last
from palette.teletalk.query.query import Query


if TYPE_CHECKING:
    from palette.teletalk.crowd.talk.talk import Talk


@dataclass
class Response:
    root_query: Optional[Query] = None
    query: Optional[Query] = None
    messages: list[Message] = field(default_factory=list)
    talk: Optional["Talk"] = None  # circular import

    @property
    def message(self) -> Optional[Message]:
        return last(self.messages, default=None)
