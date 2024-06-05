import asyncio

from aiogram.types import Message
from palette.teledo.elements import Element
from palette.teledo.start_polling import state


async def run_element(element: Element, message: Message, inplace: bool = True):
    # - Render element and edit message

    if inplace:
        await message.edit_text(**element.render().__dict__)
    else:
        await message.answer(**element.render().__dict__)

    # - Wait for interaction and get callback_info

    _id = await state["telegram_interaction"]
    callback_info = state["callback_infos"][_id]
    callback_coroutine = callback_info.callback(message=message, root=element, element=callback_info.element)

    # - Reset interaction

    state["telegram_interaction"] = asyncio.get_running_loop().create_future()

    # - Run callback

    return await callback_coroutine
