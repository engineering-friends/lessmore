from aiogram.types import CallbackQuery
from loguru import logger

from palette.teletalk.crowd.callback_event import CallbackEvent
from palette.teletalk.crowd.crowd import crowd


async def global_callback_query_handler(callback_query: CallbackQuery) -> None:
    logger.debug(
        "Callback query received",
        user_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        data=callback_query.data,
    )

    # - Get user context

    chat = crowd.get_chat(user_id=callback_query.from_user.id)

    # - Get talk with the same message id

    talk = chat.get_talk(question_message=callback_query.message)

    if not talk:
        logger.error(
            "Failed to find talk for callback query",
            user_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            callback_id=callback_query.data,
        )
        return

    # - Send callback event to the coroutine

    talk.question_event.set_result(CallbackEvent(callback_id=callback_query.data))
