from typing import Any, Callable, List


class QuestionMessage:
    def __init__(
        self,
        chat_id: int,
        on_query_reply: Callable[[Any], str],  # Callback to handle message after query reply
    ):
        self.chat_id = chat_id
        self.on_query_reply = on_query_reply

    def handle_reply(self, reply: Any) -> str:
        # - What happens after someone replies to the query

        # -- Options: keep, delete, update, custom action

        pass
