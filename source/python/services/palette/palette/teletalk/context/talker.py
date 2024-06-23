import asyncio
import uuid

from dataclasses import dataclass, field
from typing import Callable

from aiogram.types import Message

from palette.teletalk.context.talk import Talk


@dataclass
class Talker:
    user_id: int
    talks: list[Talk] = field(default_factory=list)
    active_question_messages: list[Message] = field(default_factory=list)

    def start_new_talk(self, starter_message: Message, callback: Callable):
        # - Prepare talk

        new_talk = Talk(starter_message=starter_message)

        # - Add to context

        self.talks.append(new_talk)

        # - Run

        async def _run_talk():
            # - Run callback

            await callback(message=starter_message, talk=new_talk)

            # - Remove talk

            self.talks.remove(new_talk)

        asyncio.create_task(_run_talk())
