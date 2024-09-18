import asyncio

from teletalk.app import App
from teletalk.blocks.simple_block import SimpleBlock
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    # - Test create_new and inplace modes

    await response.tell("[Test: Create new mode]")
    await response.tell("Message 1", update_mode="create_new")
    await response.tell("Message 2", update_mode="create_new")

    # - Test inplace mode

    await response.tell("[Test: Inplace mode]")
    await response.tell("Message 3 - should be updated", update_mode="create_new")
    await response.tell("Message 3", update_mode="inplace")

    # - Test text messages

    await response.tell("[Test: Inplace recent mode]")
    sample_block = SimpleBlock("Message 4 - should be updated")
    await response.tell(sample_block)
    name = await response.ask(sample_block.update("Message 4. Say anything"), update_mode="inplace_recent")
    await response.tell(sample_block.update("Message 5"), update_mode="inplace_recent")

    # - Test inplace by id

    await response.tell("[Test: Inplace by id mode]")

    sample_block = SimpleBlock()
    await response.tell(sample_block.update(text="Message 6"))
    sample_block.refresh_id()
    await response.tell(sample_block.update(text="Message 7"), update_mode="inplace_by_id")


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
