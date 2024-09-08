from aiogram.types import CallbackQuery, Message
from teletalk.query.query import Query


class Supervisor:
    def __init__(self):
        self.message_buffers_by_chat_id = {}

    def start(self):
        # - Ask default supervisor query

        pass


class SupervisorQuery(Query):
    async def on_callback_query(
        self,
        callback_query: CallbackQuery,
    ) -> None:
        # - Find the talk by message_id

        # - Send the event to the talk

        pass

    async def on_message(
        self,
        message: Message,
    ) -> None:
        # - Send the message to the buffer of the chat

        # - Close the buffer if needed

        # -- Find the talk by message_id

        # -- Send the event to the talk

        # - Create timers if needed to try to close the buffer

        pass
