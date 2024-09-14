from dataclasses import dataclass
from typing import Callable, Optional

from teletalk.models.block import Block


@dataclass
class CallbackInfo:
    callback_id: str
    callback: Callable
    block: Block
