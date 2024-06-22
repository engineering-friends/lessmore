import asyncio

from abc import ABC, abstractmethod

from aiogram.types import Message

from palette.teledo.context.context import context
from palette.teledo.elements.rendered_element import RenderedElement


class Element(ABC):
    @abstractmethod
    def render(self) -> RenderedElement:
        pass

    async def __call__(self, message: Message, inplace: bool = True):
        # - Render element and edit message

        if inplace:
            message = await message.edit_text(**self.render().__dict__)
        else:
            message = await message.answer(**self.render().__dict__)

        # - Wait for interaction and get callback_info

        _id = await context.ui_callback_id_future
        callback_info = context.ui_callbacks[_id]
        callback_coroutine = callback_info.callback(
            message=message,
            root=self,
            element=callback_info.element,
        )

        # - Reset interaction

        context.ui_callback_id_future = asyncio.get_running_loop().create_future()

        # - Run callback

        return await callback_coroutine

    @property
    def __name__(self) -> str:
        return "Element"
