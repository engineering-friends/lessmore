import hashlib
import uuid

from typing import Callable

from aiogram.types import Message
from teletalk.models.base_block import BaseBlock
from teletalk.models.block_message import BlockMessage
from teletalk.utils.generate_id import generate_id


class Page:
    def __init__(self, blocks: list[BaseBlock] = []):
        self.blocks: list[BaseBlock] = blocks

        # todo later: may create conflicts easily, when rebuilding the page with the same blocks. Is this bad? [@marklidenberg]
        if blocks:
            # - Build id as the hash of the block ids

            self.id = generate_id(hashlib.sha256(str(sorted([block.id for block in blocks])).encode()).hexdigest()[:32])
        else:
            # - Or just generate a new one

            self.id = generate_id()

    def render(self) -> list[BlockMessage]:
        return [block.render() for block in self.blocks]

    @property
    def block_messages(self) -> list[BlockMessage]:
        return [block.current_output for block in self.blocks]

    @property
    def messages(self) -> list[Message]:
        return [message for block_message in self.block_messages for message in block_message.messages]
