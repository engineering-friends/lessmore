from typing import Callable

from aiogram.types import Message
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage


class Page:
    def __init__(self, blocks: list[Block] = []):
        self.blocks: list[Block] = blocks

    def render(self) -> list[BlockMessage]:
        return [block.render() for block in self.blocks]

    @property
    def block_messages(self) -> list[BlockMessage]:
        return [block._render for block in self.blocks]

    @property
    def messages(self) -> list[Message]:
        return [message for block_message in self.block_messages for message in block_message.messages]
