from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class CallbackInfo:
    callback_id: str
    callback: Callable
