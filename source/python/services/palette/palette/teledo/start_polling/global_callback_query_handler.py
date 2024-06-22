import asyncio

from aiogram.types import CallbackQuery
from loguru import logger
from more_itertools import first

from palette.teledo.context.context import context
from palette.teledo.context.interaction import CallbackEvent


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
            if interaction.pending_question.message_id == callback_query.message.message_id
        ]
    )

    if not interaction:
        logger.debug(
            "Failed to find interaction for callback query",
            user_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            callback_id=callback_query.data,
        )

    # - Get callback

    callback = user_context.pending_question.callbacks.get(callback_query.data)

    if not callback:
        logger.debug(
            "Failed to find callback for callback query",
            user_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            callback_id=callback_query.data,
        )
        return

    # - Run callback

    asyncio.create_task(callback(interaction=interaction))

    # - Set callback id to interaction future. It will be awaited in the element coroutine

    interaction.pending_question.callback_future.set_result(
        CallbackEvent(
            type="ui",
            callback_id=callback_query.data,
        )
    )
