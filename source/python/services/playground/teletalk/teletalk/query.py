from typing import Any, List, Tuple

from teletalk.query.question_message import QuestionMessage


class Query:
    def __init__(self):
        self.children = []

    def render(self) -> Tuple[List[QuestionMessage], List[Any]]:
        pass
