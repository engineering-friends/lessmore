from typing import TYPE_CHECKING, Callable

from aiogram.types import CallbackQuery, Message
from loguru import logger
from more_itertools import last
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response
from teletalk.talk import Talk


if TYPE_CHECKING:
    from teletalk.app import App


class Dispatcher:
    def __init__(
        self,
        app: "App",
        message_starter: Callable,
        command_starters: dict[str, Callable] = {},
    ):
        """Dispatcher receives the `Response` from the user and dispatches it to the appropriate `Talk`.
        - receives the `Response`
        - collects the messages in a buffer
        - when the buffer is full, builds the response and sends it to the appropriate `Talk` or creates a new `Talk`"""

        # - Args

        self.app = app
        self.message_starter = message_starter
        self.command_starters = command_starters

        # - State

        self.message_buffers_by_chat_id: dict[str, list[Message]] = {}

    async def __call__(
        self,
        response: Response,
    ) -> None:
        # - If callback_query

        if response.callback_id:
            # - Find the `Talk` by `Response.callback_id` within the `Block`s

            talk = None
            for _talk in self.app.talks:
                for block in _talk.active_page.blocks:
                    if block.query_callbacks:
                        for callback_id, callback in block.query_callbacks.items():
                            if callback_id == response.callback_id:
                                talk = _talk
                                break

            if not talk:
                logger.info("Didn't find the `Talk` by `Response.callback_id`", response=response)

            # - Send the event to the `Talk`

            await talk.receive_response(response)

            # - Return

            return

        # - If messages

        if response.block_messages:
            assert len(response.block_messages) == 1

            response_block_message = response.block_messages[0]

            # - Add the message to the buffer

            self.message_buffers_by_chat_id.setdefault(response_block_message.chat_id, []).extend(
                response_block_message.messages
            )

            # - Check if buffer is full

            is_full = True  # make properly later

            # - Return if buffer is not full

            if not is_full:
                logger.info("Buffer is not full, keep waiting", response=response)
                return

            # - Find focused `Talk` - talk with last message in the chat

            chat_id = response_block_message.chat_id

            focused_talk = max(
                [
                    talk
                    for talk in self.app.talks
                    if [message for message in talk.history if message.chat.id == chat_id]
                ],
                key=lambda talk: last([message for message in talk.history if message.chat.id == chat_id]).date,
                default=None,
            )

            # - Close the buffer and build the `Response` with the buffer

            buffer = self.message_buffers_by_chat_id.pop(chat_id)

            buffered_response = Response(
                block_messages=[
                    BlockMessage(
                        chat_id=chat_id,
                        text="\n".join([message.text for message in buffer]),
                        messages=buffer,
                    )
                ]
            )  # todo later: properly collect block message from the buffer [@marklidenberg]

            # - Process command

            if buffer[0].text.startswith("/"):
                command = buffer[0].text.split()[0][1:]
                if command in self.command_starters:
                    logger.info("Found command", command=command)
                    await self.app.start_new_talk(
                        starter=self.command_starters[command],
                        initial_response=buffered_response,
                    )
                    return

            # - Process simple message

            # -- If no focused `Talk` found: start a new `Talk` with the message starter

            if not focused_talk:
                await self.app.start_new_talk(
                    starter=self.message_starter,
                    initial_response=buffered_response,
                )
                return

            # -- If focused `Talk` found: send the event to the `Talk`

            await focused_talk.receive_response(response=buffered_response)
