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

        pass

        # - Create new messages / delete old messages / update messages

        pass

        # - Update menus if needed

        pass

        # - Wait for the event

        pass

        # - Disable old messages UI

        pass

        # - Apply on_query_reply for each message (spawn tasks in parallel)

        pass

        # - Run and return appropriate callback with query, child_query, messages

        pass

        # -- Useful to wrap the response in a Response class

        pass
