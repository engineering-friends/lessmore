import asyncio
import uuid

from dataclasses import dataclass, field
from typing import Callable, Optional

from aiogram.types import Message

from palette.teletalk.context.question import Question


@dataclass
class Talk:
    user_id: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: dict = field(default_factory=dict)
    question: Question = field(default_factory=Question)
    sample_message: Optional[Message] = None  # used for answering to the user with in the same chat
