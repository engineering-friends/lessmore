import asyncio
import uuid

from abc import ABC, abstractmethod
from asyncio import Future
from dataclasses import dataclass
from typing import Callable, Optional

from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.aiogram_playground.elements.element import RenderedElement
from palette.teledo.callback_info import CallbackInfo
from palette.teledo.context import Context


@dataclass
class RenderedElement:
    text: str = ""
    reply_markup: Optional[InlineKeyboardMarkup] = None


class Element(ABC):
    @abstractmethod
    def render(self) -> RenderedElement:
        pass


class EmptyElement(Element):
    def render(self) -> RenderedElement:
        return RenderedElement()


def register_callback(element: Element, callback: Callable, context: Context):
    _id = str(uuid.uuid4())
    context.callbacks_infos[_id] = CallbackInfo(callback=callback, element=element)
    return _id


class ButtonElement(Element):
    def __init__(self, text: str, callback: Callable):
        self.text = text
        self.callback = callback  # will receive callback_query

    def render(self) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=self.text,
            callback_data=register_callback(
                element=self,
                callback=self.callback,
            ),
        )
        return RenderedElement(text="Button text", reply_markup=keyboard.as_markup())
