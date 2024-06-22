import asyncio
import uuid

from dataclasses import dataclass, field
from typing import Callable

from aiogram.types import Message

from palette.teledo.context.callback_info import CallbackInfo
from palette.teledo.context.interaction import Interaction
from palette.teledo.elements.element import Element


@dataclass
class UserContext:
    # - Interactions

    user_id: int

    # todo later: index properly [@marklidenberg]
    interactions: list[Interaction] = field(default_factory=list)
    active_question_message_ids: list[str] = field(default_factory=list)

    def start_new_interaction(self, message: Message, callback: Callable):
        # - Prepare interaction

        new_interaction = Interaction(user_id=message.from_user.id, sample_message=message)

        # - Add to context

        self.interactions.append(new_interaction)

        # - Run

        async def _run_callback():
            # - Run callback

            await callback(message=message, interaction=new_interaction)

            # - Remove interaction

            self.interactions.remove(new_interaction)

        asyncio.create_task(_run_callback())
