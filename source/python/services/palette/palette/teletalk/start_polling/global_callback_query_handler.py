import asyncio

from aiogram.types import CallbackQuery
from loguru import logger
from more_itertools import first, first_true

from palette.teletalk.context.callback_event import CallbackEvent
from palette.teletalk.context.context import context


async def global_callback_query_handler(callback_query: CallbackQuery) -> None:
    logger.debug(
        "Callback query received",
        user_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        data=callback_query.data,
    )

    # - Get user context

    user_context = context.get_user_context(callback_query.from_user.id)

    # - Get talk with the same message id

    talk = first_true(
        user_context.talks,
        pred=lambda talk: talk.question_message.message_id == callback_query.message.message_id,
    )

    if not talk:
        logger.error(
            "Failed to find talk for callback query",
            user_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            callback_id=callback_query.data,
        )
        return

    # - Send callback event to the coroutine

    talk.callback_future.set_result(CallbackEvent(callback_id=callback_query.data))
