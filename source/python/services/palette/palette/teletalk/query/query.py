from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from palette.teletalk.query.rendered_query import RenderedQuery


class Query(ABC):
    message_callback: Optional[Callable] = None

    @abstractmethod
    def render(self, talk: Any) -> RenderedQuery:
        pass

    @property
    def __name__(self) -> str:
        return "Query"
