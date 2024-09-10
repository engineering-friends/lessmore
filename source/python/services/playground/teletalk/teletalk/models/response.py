from asyncio import Task
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from aiogram.types import Message
from more_itertools import first, last
from palette.teletalk.query.query import Query
from teletalk.models.bundle_message import BundleMessage
from teletalk.models.multi_query import MultiQuery


if TYPE_CHECKING:
    from palette.teletalk.crowd.talk.talk import Talk


@dataclass
class Response:
    root_multi_query: Optional[MultiQuery] = None  # root query is the query that spawned the whole conversation
    root_query: Optional[Query] = None
    query: Optional[Query] = None
    talk: Optional["Talk"] = None  # circular import
    bundle_messages: list[BundleMessage] = field(default_factory=list)

    @property
    def bundle_message(self) -> Optional[BundleMessage]:
        return last(self.bundle_messages, default=None)
