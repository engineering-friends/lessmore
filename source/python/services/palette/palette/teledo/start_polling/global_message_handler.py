import asyncio
import uuid

from typing import Callable, Optional

from aiogram.types import Message
from loguru import logger
from more_itertools import first, last, only

from palette.teledo.context.callback_event import CallbackEvent
from palette.teledo.context.context import context
from palette.teledo.context.interaction import Interaction


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

        # - If starter command: start new interaction with command

        if message.text.startswith("/"):
            command = message.text.split()[0]
            if command in command_starters:
                user_context.start_new_interaction(message=message, callback=command_starters[command])
                return

        #  - If reply and replied message is a pending question: send to reply interaction

        if message.reply_to_message:
            interaction = first(
                [
                    interaction
                    for interaction in user_context.interactions
                    if interaction.question.message.id == message.reply_to_message.id
                ],
                default=None,
            )

            if interaction:
                interaction.pending_question.callback_future.set_result(CallbackEvent(message=message))
                return

        # - If there is an interaction for latest question message id: send to corresponding interaction

        latest_question_message_id = last(user_context.active_question_message_ids, default=None)

        if latest_question_message_id:
            interaction = only(
                [
                    interaction
                    for interaction in user_context.interactions
                    if interaction.ask_message_id == latest_question_message_id
                ],
                default=None,
            )
            if interaction:
                interaction.pending_question.callback_future.set_result(CallbackEvent(message=message))
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

        user_context.start_new_interaction(message=message, callback=message_starter)

    return global_message_handler
