from asyncio import Task
from dataclasses import dataclass, field

from aiogram.types import Message
from teletalk.models.bundle_message import BundleMessage


@dataclass
class RawResponse:
    callback_id: str = ""
    bundle_messages: list[BundleMessage] = field(default_factory=list)
