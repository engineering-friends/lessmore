from typing import Callable, Optional

from aiogram.types import Message
from loguru import logger


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

        # - Get latest interaction

        pass

    return global_message_handler
