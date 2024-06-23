import asyncio
import uuid

from typing import Callable, Optional

from aiogram.types import Message
from loguru import logger
from more_itertools import first, first_true, last, only

from palette.teletalk.context.callback_event import CallbackEvent
from palette.teletalk.context.context import context
from palette.teletalk.context.talk import Talk


def get_global_message_handler(
    command_starters: dict[str, Callable] = {},  # {'/start': def f(message: Message): ...}
    message_starter: Optional[Callable] = None,  # def f(message: Message): ...) -> callable:
) -> Callable:
    async def global_message_handler(message: Message) -> None:
        logger.trace(
            "Message received",
            user_id=message.from_user.id,
            message_id=message.message_id,
            text=message.text,
        )

        # - Get user context

        user_context = context.get_user_context(message.from_user.id)

        # - If starter command: start new talk with command

        if message.text.startswith("/"):
            command = message.text.split()[0]
            if command in command_starters:
                user_context.start_talk(message=message, callback=command_starters[command])
                return

        #  - If reply and replied message is a pending question: send to reply talk

        if message.reply_to_message:
            talk = first_true(
                user_context.talks,
                pred=lambda talk: talk.question_message.message_id == message.reply_to_message.message_id,
            )

            if talk:
                talk.callback_future.set_result(CallbackEvent(message=message))
                return

        # - If there is an talk for latest question message id: send to corresponding talk

        latest_question_message = last(user_context.active_question_messages, default=None)

        if latest_question_message.message_id:
            talk = first_true(
                user_context.talks,
                pred=lambda talk: talk.question_message.message_id == latest_question_message.message_id,
            )

            if talk:
                talk.callback_future.set_result(CallbackEvent(message=message))
                return

        # - Start new message by default if there is a message starter

        if not message_starter:
            # no message starter
            logger.debug(
                "No message starter",
                user_id=message.from_user.id,
                message_id=message.message_id,
                text=message.text,
            )
            return

        user_context.start_talk(message=message, callback=message_starter)

    return global_message_handler
