import asyncio

from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

# from palette.teledo.context.interaction import Interaction
from palette.teletalk.elements.rendered_element import RenderedElement


class Element(ABC):
    @abstractmethod
    def render(self, interaction: Any) -> RenderedElement:
        pass

    async def __call__(self, interaction: Any, inplace: bool = True):
        # - Reset question callbacks

        interaction.question.ui_callbacks = {}
        interaction.question.message_callback = None

        # - Render element and edit message (and register callbacks alongside of this process with interaction.register_callback)

        # todo later: return callbacks with render function instead?

        if inplace and interaction.question:
            message = await interaction.question.message.edit_text(**self.render(interaction=interaction).__dict__)
        else:
            message = await interaction.sample_message.answer(**self.render(interaction=interaction).__dict__)

            # todo later: make properly
            from palette.teletalk.context.context import context

            user_context = context.get_user_context(interaction.user_id)
            user_context.active_question_messages.append(message)

        # - Update pending question message

        interaction.question.message = message

        # - Wait for interaction and get callback_info

        callback_event = await interaction.question.callback_future

        if callback_event.callback_id:
            # UI event
            if callback_event.callback_id not in interaction.question.ui_callbacks:
                logger.error("Callback not found", callback_id=callback_event.callback_id)
                return

            callback_info = interaction.question.ui_callbacks[callback_event.callback_id]
            callback_coroutine = callback_info.callback(
                message=message,
                root=self,
                element=callback_info.element,
            )
        else:
            # Message event

            if not interaction.question.message_callback:
                logger.debug("Message callback not found, skipping")
                return

            callback_info = interaction.question.message_callback
            callback_coroutine = callback_info.callback(
                message=message,
                root=self,
            )

        # - Reset interaction future

        interaction.question.callback_future = asyncio.get_running_loop().create_future()

        # - Run callback

        return await callback_coroutine

    @property
    def __name__(self) -> str:
        return "Element"
