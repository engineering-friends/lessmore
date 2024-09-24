from dataclasses import dataclass
from typing import Callable


@dataclass
class CallbackInfo:
    callback: Callable
    callback_id: str
    callback_text: str = ""
