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
    messages: Optional[Message] = None

    # - Enriched response

    root_query: Optional[Query] = None
    query: Optional[Query] = None
    talk: Optional["Talk"] = None  # circular import
