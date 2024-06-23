import asyncio
import uuid

from typing import Callable, Optional

from aiogram.types import Message
from loguru import logger
from more_itertools import first, first_true, last, only

from palette.teletalk.crowd.callback_event import CallbackEvent
from palette.teletalk.crowd.crowd import crowd
from palette.teletalk.crowd.talk import Talk


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

        talker = crowd.get_talker(user_id=message.from_user.id)

        # - If starter command: start new talk with command

        if message.text.startswith("/"):
            command = message.text.split()[0]
            if command in command_starters:
                talker.start_new_talk(starter_message=message, callback=command_starters[command])
                return

        #  - If reply and replied message is a pending question: send to reply talk

        if message.reply_to_message:
            talk = talker.get_talk(question_message=message.reply_to_message)

            if talk:
                talk.event.set_result(CallbackEvent(message=message))
                return

        # - If there is an talk for latest question message id: send to corresponding talk

        latest_question_message = last(talker.active_question_messages, default=None)

        if latest_question_message.message_id:
            talk = talker.get_talk(latest_question_message.message_id)

            if talk:
                talk.event.set_result(CallbackEvent(message=message))
                return

        # - Start new message by default if there is a message starter

        if not message_starter:
            logger.debug(
                "No message starter",
                user_id=message.from_user.id,
                message_id=message.message_id,
                text=message.text,
            )
            return

        talker.start_new_talk(starter_message=message, callback=message_starter)

    return global_message_handler
