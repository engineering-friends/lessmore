import asyncio

from typing import Callable, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger
from palette.teledo.archive.thread_handler import thread_handler
from palette.teledo.context import context


async def global_callback_query_handler(callback_query: CallbackQuery) -> None:
    logger.debug(
        "Callback query received",
        user_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        data=callback_query.data,
    )

    # - get interaction

    interaction = context.interactions_by_user_id.get(callback_query.from_user.id, {}).get(
        callback_query.message.message_id
    )

    # - Case if interaction is not found

    if not interaction:
        logger.debug(
            "Failed to find interaction for callback query",
            user_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            callback_id=callback_query.data,
        )

    # - Set callback id to interaction future. It will be awaited in the element coroutine

    interaction.ui_callback_id_future.set_result(callback_query.data)


async def global_message_handler(message: Message) -> None:
    logger.debug(
        "Message received",
        user_id=message.from_user.id,
        message_id=message.message_id,
        text=message.text,
    )
