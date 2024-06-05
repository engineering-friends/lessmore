import asyncio

from aiogram.types import Message
from palette.teledo.context import Context, context
from palette.teledo.elements.element import Element


async def run_element(element: Element, message: Message, inplace: bool = True):
    # - Render element and edit message

    if inplace:
        message = await message.edit_text(**element.render().__dict__)
    else:
        message = await message.answer(**element.render().__dict__)

    # - Wait for interaction and get callback_info

    _id = await context.callback_id_future
    callback_info = context.callbacks_infos[_id]
    callback_coroutine = callback_info.callback(message=message, root=element, element=callback_info.element)

    # - Reset interaction

    context.callback_id_future = asyncio.get_running_loop().create_future()

    # - Run callback

    return await callback_coroutine
