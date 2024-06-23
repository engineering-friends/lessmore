import asyncio

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from loguru import logger

# from palette.teledo.crowd.talk import talk
from palette.teletalk.elements.rendered_element import RenderedElement


class Element(ABC):
    message_callback: Optional[Callable] = None

    @abstractmethod
    def render(self, talk: Any) -> RenderedElement:
        pass

    async def __call__(self, talk: Any, inplace: bool = True):
        # - Reset question callbacks

        talk.callbacks = {}

        # - Render element and edit message (and register callbacks alongside of this process with talk.register_callback)

        # todo later: return callbacks with render function instead? [@marklidenberg]

        if inplace and talk:
            message = await talk.question_message.edit_text(**self.render(talk=talk).__dict__)
        else:
            message = await talk.starter_message.answer(**self.render(talk=talk).__dict__)

            # todo later: make properly [@marklidenberg]
            from palette.teletalk.crowd.crowd import crowd

            talker = crowd.get_talker(talk.starter_message.from_user.id)
            talker.active_question_messages.append(message)

        # - Update pending question message

        talk.question_message = message

        # - Wait for talk and get callback_info

        callback_event = await talk.event

        if callback_event.callback_id:
            # - UI event

            if callback_event.callback_id not in talk.callbacks:
                logger.error("Callback not found", callback_id=callback_event.callback_id)
                return

            callback_info = talk.callbacks[callback_event.callback_id]
            callback_coroutine = callback_info.callback(
                message=message,
                root=self,
                element=callback_info.element,
            )
        else:
            # - Message event

            if not self.message_callback:
                logger.debug("Message callback not found, skipping")
                return

            callback_coroutine = self.message_callback(
                message=message,
                root=self,
                element=self,
            )

        # - Reset talk future

        talk.event = asyncio.get_running_loop().create_future()

        # - Run callback

        return await callback_coroutine

    @property
    def __name__(self) -> str:
        return "Element"
