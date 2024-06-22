import asyncio

from dataclasses import dataclass, field
from typing import Callable

from aiogram.types import Message

from palette.teledo.context.interaction import Interaction


@dataclass
class UserContext:
    # - Interactions

    user_id: int

    # todo later: index properly [@marklidenberg]
    interactions: list[Interaction] = field(default_factory=list)
    active_question_message_ids: list[str] = field(default_factory=list)

    def start_new_interaction(self, message: Message, callback: Callable):
        # - Prepare interaction

        new_interaction = Interaction(user_id=message.from_user.id)

        # - Add to context

        self.interactions.append(new_interaction)

        # - Run

        asyncio.create_task(callback(message=message, interaction=new_interaction))


@dataclass
class Context:
    user_contexts: dict[str, UserContext] = field(default_factory=dict)
    callbacks: dict = field(default_factory=dict)
