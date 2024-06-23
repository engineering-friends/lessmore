from dataclasses import dataclass
from typing import Callable, Optional

from palette.teletalk.query.query import Query


@dataclass
class CallbackInfo:
    callback: Callable
    query: Optional[Query]
