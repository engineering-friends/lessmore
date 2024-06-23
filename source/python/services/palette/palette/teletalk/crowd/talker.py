import asyncio

from asyncio import Task
from dataclasses import dataclass, field
from typing import Any, Callable

from aiogram.types import Message

from palette.teletalk.crowd.talk import Talk


@dataclass
class Talker:
    talks: list[Talk] = field(default_factory=list)
    active_question_messages: list[Message] = field(default_factory=list)

    def start_new_talk(self, starter_message: Message, callback: Callable) -> Task:
        # - Prepare talk

        new_talk = Talk(talker=self, starter_message=starter_message)

        # - Add to context

        self.talks.append(new_talk)

        # - Run

        async def _run_talk():
            # - Run callback

            await callback(talk=new_talk, message=starter_message)

            # - Remove talk

            self.talks.remove(new_talk)

        return asyncio.create_task(_run_talk())

    def get_talk(self, question_message: Message, default: Any = None) -> Talk:
        return next(
            (
                talk
                for talk in self.talks
                if talk.question_message and talk.question_message.message_id == question_message.message_id
            ),
            default,
        )
