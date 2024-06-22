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
    callbacks: dict = field(default_factory=dict)

    def start_new_interaction(self, message: Message, callback: Callable):
        # - Prepare interaction

        new_interaction = Interaction(user_id=message.from_user.id)

        # - Add to context

        self.interactions.append(new_interaction)

        # - Run

        async def _run_callback():
            # - Run callback

            await callback(message=message, interaction=new_interaction)

            # - Remove interaction

            self.interactions.remove(new_interaction)

        asyncio.create_task(_run_callback())
