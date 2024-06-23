from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from palette.teletalk.elements.rendered_element import RenderedElement


class Element(ABC):
    message_callback: Optional[Callable] = None

    @abstractmethod
    def render(self, talk: Any) -> RenderedElement:
        pass

    @property
    def __name__(self) -> str:
        return "Element"
