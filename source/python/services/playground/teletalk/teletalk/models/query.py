import uuid

from typing import Any, Callable, List, Optional, Tuple

from teletalk.bundle_message import BundleMessage


class Query:
    """Bundle is a collection of messages grouped together in telegram (like album)"""

    def __init__(self, chat_id: str):
        # - Init

        self.chat_id = chat_id

        # - Tree

        self.parent: Optional["Query"] = None
        self.children: list["Query"] = []

        # - Callbacks

        message_callback: Optional[Callable] = None  # def message_callback(response: Response) -> None
        on_query_reply: Optional[Callable] = (
            None  # what to do with the messages after the query reply, def on_query_reply(bundle_messages: list[BundleMessage]) -> None
        )

    def render(self, callback_wrapper: Callable) -> BundleMessage:
        raise NotImplementedError
