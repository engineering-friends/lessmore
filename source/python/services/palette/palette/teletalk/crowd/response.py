from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

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

    talk: Optional["Talk"] = None  # recursive import
    root_query: Optional[Query] = None
    query: Optional[Query] = None
