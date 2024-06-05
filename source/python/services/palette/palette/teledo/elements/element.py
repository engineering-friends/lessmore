from abc import ABC, abstractmethod

from palette.teledo.elements.rendered_element import RenderedElement


class Element(ABC):
    @abstractmethod
    def render(self) -> RenderedElement:
        pass
