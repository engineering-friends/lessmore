from asyncio import Future
from typing import Any, Callable, List


class Talk:
    def __init__(self, starter: Callable):
        self.starter = starter  # Coroutine starter for the talk
        self.question_messages = []  # List of messages related to ongoing queries
        self.history = []  # History of interactions within the talk
        self.event = Future()  # Future to manage asynchronous events

    def ask(self, query: str) -> Any:
        # - Render query messages and menus

        # - Create new messages / delete old messages / update messages

        # - Update menus if needed

        # - Wait for the event

        # - Disable old messages UI

        # - Apply on_query_reply for each message (spawn tasks in parallel)

        # - Run and return appropriate callback with query, child_query, messages

        # -- Useful to wrap the response in a Response class

        pass
