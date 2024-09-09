from asyncio import Future
from typing import Any, Callable, List, Literal

from teletalk.query.query import Query


class Talk:
    def __init__(self, starter: Callable):
        self.starter = starter  # Coroutine starter for the talk
        self.question_messages = []  # List of messages related to ongoing queries
        self.menus = []  # List of menus related to ongoing queries (for different chats)
        self.history = []  # History of interactions within the talk
        self.event = Future()  # Future to manage asynchronous events

    def ask(
        self,
        query: Query,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
    ) -> Any:
        # - Render the query messages and menus, update `self.question_messages` and `self.menus`

        # - Update messages in telegram according to the update_mode. Add new messages to `self.question_messages and self.history`

        # - Wait for the response event from the global callbacks

        # - Disable old messages UI

        # - Apply `on_query_reply` for each message (spawn tasks in parallel)

        # - Run and return appropriate callback with query, child_query, messages

        # -- Useful to wrap the response in a `Response` class

        pass

    def tell(self, **kwargs) -> None:
        # - Send the messages and add them to the `self.history`

        pass
