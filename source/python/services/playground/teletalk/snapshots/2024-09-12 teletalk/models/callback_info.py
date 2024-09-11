from dataclasses import dataclass
from typing import Callable, Optional

from teletalk.models.query import Query


@dataclass
class CallbackInfo:
    callback_id: str
    callback: Callable
    query: Query
