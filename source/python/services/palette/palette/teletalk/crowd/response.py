from dataclasses import dataclass
from typing import Optional

from aiogram.types import Message


@dataclass
class Response:
    callback_id: str = ""
    message: Optional[Message] = None
