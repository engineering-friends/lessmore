import asyncio

from asyncio import Future
from typing import Any, Callable, Coroutine, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from palette.teledo.context import context
from palette.teledo.start_polling.thread_handler import thread_handler


async def global_callback_handler(callback_query: CallbackQuery) -> None:
    context.callback_id_future.set_result(callback_query.data)


async def start_polling(
    bot: Bot | str,
    command_handlers: dict,
    message_handler: Optional[Callable] = None,
    default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
) -> None:
    # - Init dispatcher

    dp = Dispatcher()

    # - Init future

    context.callback_id_future = asyncio.get_running_loop().create_future()

    # - Register handlers

    for command, handler in command_handlers.items():
        dp.message.register(
            thread_handler(handler=handler),
            Command(command),
        )

    if message_handler:
        dp.message.register(
            thread_handler(handler=message_handler),
        )

    dp.callback_query.register(global_callback_handler)

    # - Init bot from token if needed

    if isinstance(bot, str):
        bot = Bot(
            token=bot,
            default=default_bot_properties,
        )

    # - Start polling

    await dp.start_polling(bot)
