import asyncio

from asyncio import Task
from dataclasses import dataclass, field
from typing import Any, Callable

from aiogram.types import Message
from loguru import logger

from palette.teletalk.crowd.talk import Talk
from palette.teletalk.elements.element import Element


@dataclass
class Chat:
    talks: list[Talk] = field(default_factory=list)
    question_messages: list[Message] = field(default_factory=list)

    def start_new_talk(self, starter_message: Message, callback: Callable) -> Task:
        # - Prepare talk

        new_talk = Talk(chat=self, starter_message=starter_message)

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

    async def ask(self, talk: Talk, element: Element, inplace: bool = True):
        # - Render element and edit message (and register callbacks alongside of this process with talk.register_callback)

        if inplace and talk.question_message:
            message = await talk.question_message.edit_text(**element.render(talk=talk).__dict__)
        else:
            message = await talk.starter_message.answer(**element.render(talk=talk).__dict__)
            self.question_messages.append(message)

        # - Update pending question message

        talk.set_question_message(message)

        # - Wait for talk and get callback_info

        while True:
            callback_event = await talk.wait_for_question_event()

            if callback_event.callback_id:
                # - UI event

                if callback_event.callback_id not in talk.question_callbacks:
                    logger.error("Callback not found", callback_id=callback_event.callback_id)
                    continue

                callback_info = talk.question_callbacks[callback_event.callback_id]
                callback_coroutine = callback_info.callback(
                    talk=talk,
                    root=element,
                    element=callback_info.element,
                )
                break
            else:
                # - Message event

                if not element.message_callback:
                    logger.debug("Message callback not found, skipping")
                    continue

                callback_coroutine = element.message_callback(
                    talk=talk,
                    message=callback_event.message,
                )
                break

        # - Run callback

        return await callback_coroutine
