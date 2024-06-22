from aiogram.types import CallbackQuery
from loguru import logger

from palette.teledo.context.context import context
from palette.teledo.context.interaction import CallbackEvent


async def global_callback_query_handler(callback_query: CallbackQuery) -> None:
    logger.debug(
        "Callback query received",
        user_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        data=callback_query.data,
    )

    # - Get interaction

    interaction = context.user_interactions.get(callback_query.from_user.id, {}).get(callback_query.message.message_id)

    # - Case if interaction is not found

    if not interaction:
        logger.debug(
            "Failed to find interaction for callback query",
            user_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            callback_id=callback_query.data,
        )

    # - Set callback id to interaction future. It will be awaited in the element coroutine

    interaction.pending_question.callback_future.set_result(
        CallbackEvent(
            type="ui",
            callback_id=callback_query.data,
        )
    )
