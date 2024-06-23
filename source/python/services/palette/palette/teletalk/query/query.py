from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from palette.teletalk.query.rendered_query import RenderedQuery


class Query(ABC):
    @abstractmethod
    def render(self, talk: Any) -> RenderedQuery:
        pass
