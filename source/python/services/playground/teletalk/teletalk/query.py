import uuid

from typing import Any, Callable, List, Tuple

from teletalk.callback_info import CallbackInfo
from teletalk.question_message import QuestionMessage


class Query:
    def __init__(self):
        self.children = []

    def render(self, callback_wrapper: Callable) -> Tuple[List[QuestionMessage], List[Any]]:
        pass
