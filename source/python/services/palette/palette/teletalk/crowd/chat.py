import asyncio

from asyncio import Task
from dataclasses import dataclass, field
from typing import Any, Callable

from aiogram.types import Message
from loguru import logger

from palette.teletalk.crowd.talk import Talk
from palette.teletalk.query.query import Query


@dataclass
class Chat:
    talks: list[Talk] = field(default_factory=list)

    def start_new_talk(self, starter_message: Message, callback: Callable) -> Task:
        # - Prepare talk

        new_talk = Talk(
            chat=self,
            starter_message=starter_message,
            is_bot_thinking=True,
        )

        # - Add talk

        self.talks.append(new_talk)

        # - Run

        async def _run_talk():
            # - Run callback

            await callback(talk=new_talk, message=starter_message)

            # - Set bot thinking to false (not really necessary, just for the sake of cleaning up the talk)

            new_talk.set_bot_thinking(False)

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
