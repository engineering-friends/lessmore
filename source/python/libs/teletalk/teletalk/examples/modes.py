import asyncio

from teletalk.app import App
from teletalk.blocks.simple_block import SimpleBlock
from teletalk.models.page import Page
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    # - Test create_new and inplace modes

    await response.tell("[Test: Create new mode]")
    await response.tell("Message 1", mode="create_new")
    await response.tell("Message 2", mode="create_new")

    # - Test inplace mode

    await response.tell("[Test: Inplace mode]")
    await response.tell("Message 3 - should be updated", mode="create_new")
    await response.tell("Message 3", mode="inplace")

    # - Test text messages

    await response.tell("[Test: Inplace recent mode]")
    sample_block = SimpleBlock("Message 4 - should be updated")
    await response.tell(sample_block)
    name = await response.ask(sample_block.update("Message 4. Say anything"), mode="inplace_recent")
    await response.tell(sample_block.update("Message 5"), mode="inplace_recent")

    # - Test inplace by id

    await response.tell("[Test: Inplace by id mode]")

    sample_block = SimpleBlock()
    await response.tell(sample_block.update(text="Message 6"))
    sample_block.refresh_id()
    await response.tell(sample_block.update(text="Message 7 - should be updated"), mode="inplace_by_id")
    await response.tell(sample_block.update(text="Message 7"), mode="inplace_by_id")

    # - Test inplace by id with 2 messages

    await response.tell("[Test: Inplace by id with 2 messages]")

    page = Page(
        blocks=[
            SimpleBlock(text="Message 8"),
            SimpleBlock(text="Message 9 - should be updated"),
        ]
    )

    await response.tell(page)
    page.blocks[0].text = "Message 10"
    page.blocks[0].refresh_id()
    page.blocks[1].text = "Message 9"
    await response.tell(page, mode="inplace_by_id")


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()