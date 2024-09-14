from typing import Callable

from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage


class Page:
    def __init__(self):
        self.blocks: list[Block] = []

    def render(self, callback_wrapper: Callable) -> list[BlockMessage]:
        return [block.render(callback_wrapper=callback_wrapper) for block in self.blocks]
