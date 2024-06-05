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
        self.callback = callback

    def render(self) -> RenderedElement:
        keyboard = InlineKeyboardBuilder()
        state["callbacks"]["button"] = self.callback
        keyboard.button(text=self.text, callback_data="button")
        return RenderedElement(text="Button text", reply_markup=keyboard.as_markup())


async def run_element(element: Element, message: Message):
    # - Render element and edit message

    await message.edit_text(**element.render().__dict__)

    # - Wait for interaction

    callback = await state["telegram_interaction"]

    # - Run callback

    return await callback()


async def start(message: Message) -> None:
    await message.answer(f"Hello, Mark Lidenberg!")
    await asyncio.sleep(3)

    async def callback():
        await message.answer("Button clicked!")


async def echo(message: Message) -> None:
    await message.answer(message.text[::-1])


async def main() -> None:
    await start_polling(
        bot=init_deps().config.telegram_bot_token,
        command_handlers={
            "start": start,
            "echo": echo,
        },
        message_handler=echo,
    )


if __name__ == "__main__":
    asyncio.run(main())
