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
from palette.teledo.element_primitives import Element
from palette.teledo.register_callback import register_callback


class EmptyElement(Element):
    def render(self, context: Context) -> RenderedElement:
        return RenderedElement()


class ButtonElement(Element):
    def __init__(self, text: str, callback: Callable):
        self.text = text
        self.callback = callback  # will receive callback_query

    def render(self, context: Context) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=self.text,
            callback_data=register_callback(
                element=self,
                callback=self.callback,
                context=context,
            ),
        )
        return RenderedElement(text="Button text", reply_markup=keyboard.as_markup())
