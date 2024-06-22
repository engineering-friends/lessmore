import asyncio

from abc import ABC, abstractmethod

from loguru import logger

from palette.teledo.context.context import context
from palette.teledo.context.interaction import Interaction
from palette.teledo.elements.rendered_element import RenderedElement


class Element(ABC):
    @abstractmethod
    def render(self) -> RenderedElement:
        pass

    async def __call__(self, interaction: Interaction, inplace: bool = True):
        # - Reset question callbacks

        interaction.pending_question.ui_callbacks = {}
        interaction.pending_question.message_callback = None

        # - Render element and edit message (and register callbacks alongside of this process with interaction.register_callback)

        # todo later: return callbacks with render function instead?

        if inplace and interaction.pending_question:
            message = await interaction.pending_question.message.edit_text(**self.render().__dict__)
        else:
            message = await interaction.sample_message.answer(**self.render().__dict__)

        # - Update pending question message

        interaction.pending_question.message = message

        # - Wait for interaction and get callback_info

        callback_event = await interaction.pending_question.callback_future

        if callback_event.callback_id:
            # UI event
            if callback_event.callback_id not in context.ui_callbacks:
                logger.error("Callback not found", callback_id=callback_event.callback_id)
                return

            callback_info = context.ui_callbacks[callback_event.callback_id]
            callback_coroutine = callback_info.callback(
                message=message,
                root=self,
                element=callback_info.element,
            )
        else:
            # Message event

            if not interaction.pending_question.message_callback:
                logger.debug("Message callback not found, skipping")
                return

            callback_info = context.ui_callbacks[callback_event.callback_id]
            callback_coroutine = callback_info.callback(
                message=message,
                root=self,
                element=callback_info.element,
            )

        # - Reset interaction future

        interaction.pending_question.callback_future = asyncio.get_running_loop().create_future()

        # - Run callback

        return await callback_coroutine

    @property
    def __name__(self) -> str:
        return "Element"
