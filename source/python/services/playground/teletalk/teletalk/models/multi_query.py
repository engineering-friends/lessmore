from typing import Callable

from teletalk.models.bundle_message import BundleMessage
from teletalk.models.query import Query


class MultiQuery:
    def __init__(self):
        self.queries: list[Query] = []

    def render(self, callback_wrapper: Callable) -> list[BundleMessage]:
        return [query.render(callback_wrapper=callback_wrapper) for query in self.queries]
