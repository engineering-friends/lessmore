import asyncio

from typing import Callable

from teletalk.app import App
from teletalk.blocks.simple_block import SimpleBlock
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    button = SimpleBlock(inline_keyboard_markup=[["Click me!"]])


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
