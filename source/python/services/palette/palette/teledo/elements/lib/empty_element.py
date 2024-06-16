from palette.aiogram_playground.elements.element import RenderedElement
from palette.teledo.elements.element import Element


class EmptyElement(Element):
    def render(self) -> RenderedElement:
        return RenderedElement()
