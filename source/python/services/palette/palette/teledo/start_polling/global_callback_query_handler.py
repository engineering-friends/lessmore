import asyncio

from aiogram.types import CallbackQuery
from loguru import logger
from more_itertools import first

from palette.teledo.context.callback_event import CallbackEvent
from palette.teledo.context.context import context


async def global_callback_query_handler(callback_query: CallbackQuery) -> None:
    logger.debug(
        "Callback query received",
        user_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        data=callback_query.data,
    )

    # - Get user context

    user_context = context.get_user_context(callback_query.from_user.id)

    # - Get interaction

    interaction = first(
        [
            interaction
            for interaction in user_context.interactions
            if interaction.question.message.message_id == callback_query.message.message_id
        ],
        default=None,
    )

    if not interaction:
        logger.debug(
            "Failed to find interaction for callback query",
            user_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            callback_id=callback_query.data,
        )
        return

    # - Set callback id to interaction future. It will be awaited in the element coroutine

    interaction.question.callback_future.set_result(CallbackEvent(callback_id=callback_query.data))
