import asyncio

from teletalk.app import App
from teletalk.blocks.simple_block import SimpleBlock
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    # - Test text messages

    sample_block = SimpleBlock("should_be_deleted")
    await response.tell(sample_block)
    name = await response.ask(sample_block.update("What is your name?"), update_mode="inplace_recent")
    age = await response.ask(sample_block.update("How old are you?"), update_mode="inplace_recent")
    await response.tell(f"Hello, {name}! You are {age} years old :)")


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
