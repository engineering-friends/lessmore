import asyncio

from aiogram.types import Message
from palette.teledo.context import Context
from palette.teledo.elements import Element


async def run_element(element: Element, message: Message, context: Context, inplace: bool = True):
    # - Render element and edit message

    if inplace:
        message = await message.edit_text(**element.render(context=context).__dict__)
    else:
        message = await message.answer(**element.render(context=context).__dict__)

    print(message)
    # - Wait for interaction and get callback_info

    _id = await context.telegram_interaction
    callback_info = context.callbacks_infos[_id]
    callback_coroutine = callback_info.callback(message=message, root=element, element=callback_info.element)

    # - Reset interaction

    context.telegram_interaction = asyncio.get_running_loop().create_future()

    # - Run callback

    return await callback_coroutine
