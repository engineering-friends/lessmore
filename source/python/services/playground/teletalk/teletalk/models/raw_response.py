from asyncio import Task
from dataclasses import dataclass, field

from aiogram.types import Message
from teletalk.models.block_message import BlockMessage


@dataclass
class RawResponse:
    callback_id: str = ""
    block_messages: list[BlockMessage] = field(default_factory=list)
