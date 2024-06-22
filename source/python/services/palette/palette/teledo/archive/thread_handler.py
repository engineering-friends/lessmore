from typing import Any, Callable

from aiogram.types import Message
from palette.teledo.context.context import context


def thread_handler(handler: Callable) -> Callable:
    async def wrapper(message: Message) -> Any:
        # - Check if thread is already started

        if context.thread_messages:
            await message.answer("Another thread is already started!")
            return

        # - Start thread

        context.thread_messages = [message]

        # - Do the thread

        result = await handler(message=message)

        # - Close thread

        context.thread_messages = []

        # - Return result

        return result

    return wrapper
