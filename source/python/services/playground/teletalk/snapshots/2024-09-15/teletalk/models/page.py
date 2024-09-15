from typing import Callable

from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage


class Page:
    def __init__(self):
        self.blocks: list[Block] = []

    def render(self) -> list[BlockMessage]:
        return [block.render() for block in self.blocks]
