import asyncio

from functools import partial

from teletalk.app import App
from teletalk.blocks.block import Block
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def spawn(response: Response):
    await response.start_new_talk(
        starter=starter,
        initial_response=response,
        parallel=True,
    )
    return await response.ask(response, mode="inplace")


async def starter(response: Response):
    return await response.ask(
        Block(
            "Click to spawn another talk",
            inline_keyboard=[
                [
                    ("New talk!", spawn),
                    ("Kill me!", lambda response: response.purge_talk()),
                ]
            ],
        )
    )


def test():
    deps = TestDeps.load()
    asyncio.run(
        App().run(
            bot=deps.config.telegram_bot_token,
            starters={deps.config.telegram_test_chat_id: starter},
            message_starter=starter,
        )
    )


if __name__ == "__main__":
    test()
