from palette.teletalk.elements.element import Element
from palette.teletalk.elements.rendered_element import RenderedElement


class EmptyElement(Element):
    def render(self) -> RenderedElement:
        return RenderedElement()
