import asyncio

from typing import Callable, Optional

from aiogram.types import Message
from loguru import logger
from more_itertools import first, last, only

from palette.teledo.context.context import context
from palette.teledo.context.user_context import UserContext


def get_global_message_handler(
    command_starters: dict[str, Callable] = {},  # {'/start': def f(message: Message): ...}
    message_starter: Optional[Callable] = None,  # def f(message: Message): ...) -> callable:
) -> Callable:
    async def global_message_handler(message: Message) -> None:
        """Global message handler

        - If unknown command: skip it
        - If starter command: start the conversation
        - If no active question: run message_starter
        - If reply: send to reply interaction
        - If active question: send to active question interaction

        """
        logger.trace(
            "Message received",
            user_id=message.from_user.id,
            message_id=message.message_id,
            text=message.text,
        )

        # - Get user context

        user_context = context.get_user_context(message.from_user.id)

        # - Get latest question message

        latest_question_message_id = last(user_context.active_question_message_ids)

        # - If message is a command - process with command starter

        if message.text.startswith("/"):
            command = message.text.split()[0]
            if command in command_starters:
                # - Start interaction
                asyncio.create_task(command_starters[command](message))
            else:
                logger.trace("Unknown command", command=command)

            return

        # - If no active question - process with message starter

        if not latest_question_message_id:
            if message_starter:
                # - Start interaction
                asyncio.create_task(message_starter(message))
            else:
                logger.trace("No active question and no message starter, skipping message")

            return

        # - If active question - process with active question interaction

        interaction = only(
            [
                interaction
                for interaction in user_context.interactions
                if interaction.ask_message_id == latest_question_message_id
            ]
        )

    return global_message_handler
