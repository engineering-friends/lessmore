import hashlib
import uuid

from typing import Callable

from aiogram.types import Message
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage


class Page:
    def __init__(self, blocks: list[Block] = []):
        self.blocks: list[Block] = blocks

        # todo later: may create conflicts easily, when rebuilding the page with the same blocks. Is this bad? [@marklidenberg]
        if blocks:
            # - Build id as the hash of the block ids
            self.id = uuid.UUID(hashlib.sha256(str(sorted([block.id for block in blocks])).encode()).hexdigest()[:32])
        else:
            # - Or just generate a new one
            self.id = str(uuid.uuid4())

    def render(self) -> list[BlockMessage]:
        return [block.render() for block in self.blocks]

    @property
    def block_messages(self) -> list[BlockMessage]:
        return [block.current_output for block in self.blocks]

    @property
    def messages(self) -> list[Message]:
        return [message for block_message in self.block_messages for message in block_message.messages]