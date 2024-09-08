from aiogram.types import CallbackQuery, Message
from teletalk.query.query import Query
from teletalk.response import Response
from teletalk.talk import Talk


class Supervisor:
    def __init__(self, talks: list[Talk]):
        self.talks = talks

    def start(self):
        # - Ask default supervisor query

        pass


class SupervisorQuery(Query):
    async def on_message(
        self,
        response: Response,
    ) -> None:
        # - Find the talk by message_id

        # - Send the event to the talk

        pass
