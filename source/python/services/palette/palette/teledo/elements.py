import asyncio

from abc import ABC, abstractmethod
from asyncio import Future
from dataclasses import dataclass
from typing import Callable, Optional

from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.aiogram_playground.elements.element import RenderedElement
from palette.deps.init_deps import init_deps
from palette.teledo.start_polling import start_polling, state


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


class ButtonElement(Element):
    def __init__(self, text: str, callback: Callable):
        self.text = text
        self.callback = callback  # will receive callback_query

    def render(self) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()
        state["callbacks"]["button"] = self.callback
        keyboard.button(text=self.text, callback_data="button")
        return RenderedElement(text="Button text", reply_markup=keyboard.as_markup())


async def run_element(element: Element, message: Message):
    # - Render element and edit message

    await message.answer(**element.render().__dict__)

    # - Wait for interaction

    callback_coroutine = await state["telegram_interaction"]

    # - Run callback

    return await callback_coroutine
