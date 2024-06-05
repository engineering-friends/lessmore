import asyncio

from asyncio import Future
from typing import Any, Callable, Coroutine, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger
from palette.teledo.context import context


def thread_handler(handler: Callable) -> Callable:
    async def wrapper(message: Message) -> Any:
        # - Check if thread is already started

        if context.thread_messages:
            await message.answer("Another thread is already started!")
            return

        # - Start thread

        logger.info("Started a new thread!")

        context.thread_messages = [message]

        # - Do the thread

        result = await handler(message=message)

        # - Close thread

        context.thread_messages = []

        logger.info("Closed the thread!")

        # - Return result

        return result

    return wrapper
