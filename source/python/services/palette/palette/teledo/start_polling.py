from asyncio import Future
from typing import Any, Callable, Coroutine, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger


state = {
    "thread_messages": [],
    "callbacks": {},
    "telegram_interaction": Future(),
}


def thread_handler(async_func: Callable) -> Callable:
    async def wrapper(message: Message) -> Any:
        # - Check if thread is already started

        if state["thread_messages"]:
            await message.answer("Another thread is already started!")
            return

        # - Start thread

        logger.info("Started a new thread!")

        state["thread_messages"] = [message]

        # - Do the thread

        result = await async_func(message)

        # - Close thread

        state["thread_messages"] = []

        logger.info("Closed the thread!")

        # - Return result

        return result

    return wrapper


async def global_callback_handler(callback_query: CallbackQuery) -> None:
    logger.debug("Global callback handler called", callback_data=callback_query.data)

    # - Get callback from data

    callback = state["callbacks"][callback_query.data]

    # - Add callback to telegram_interaction future

    state["telegram_interaction"].set_result(callback(callback_query))


async def start_polling(
    bot: Bot | str,
    command_handlers: dict,
    message_handler: Optional[Callable] = None,
    default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
) -> None:
    # - Init dispatcher

    dp = Dispatcher()

    # - Register handlers

    for command, handler in command_handlers.items():
        dp.message.register(thread_handler(handler), Command(command))

    if message_handler:
        dp.message.register(thread_handler(message_handler))

    dp.callback_query.register(global_callback_handler)

    # - Init bot from token if needed

    if isinstance(bot, str):
        bot = Bot(
            token=bot,
            default=default_bot_properties,
        )

    # - Start polling

    await dp.start_polling(bot)
