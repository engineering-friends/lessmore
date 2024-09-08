from typing import Any, Callable, List


class QuestionMessage:
    def __init__(self, layout: Any, on_query_reply: Callable[[Any], str]):
        self.layout = layout  # TelegramLayout or similar layout object
        self.on_query_reply = on_query_reply  # Callback to handle message after query reply

    def handle_reply(self, reply: Any) -> str:
        # - What happens after someone replies to the query
        # -- Options: keep, delete, update, custom action

        pass


class Query:
    def __init__(self):
        self.children = []  # Child queries if applicable

    def get_question_messages(self) -> List[QuestionMessage]:
        # - Get the list of QuestionMessages (possibly across multiple chats)

        pass

        # -- Each QuestionMessage should have layout and on_query_reply callback

        pass

    def get_menus(self) -> List[Any]:
        # - Retrieve menus (possibly across multiple chats)

        pass
