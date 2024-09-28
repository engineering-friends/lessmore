import asyncio

from teletalk.app import App
from teletalk.blocks.basic_block import BasicBlock
from teletalk.models.page import Page
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    # - Test create_new and inplace modes

    await response.tell("[Test: Create new mode]")
    await response.tell("Message 1", mode="create_new")  # default
    await response.tell("Message 2", mode="create_new")  # default

    # - Test inplace mode

    await response.tell("[Test: Inplace mode]")
    await response.tell("Message 3 - should be updated", mode="create_new")
    await response.tell("Message 3", mode="inplace")

    # - Test text messages

    await response.tell("[Test: Inplace recent mode]")
    sample_block = BasicBlock("Message 4 - should be updated")
    await response.tell(sample_block)
    name = await response.ask(sample_block.update("Message 4. Say anything"), mode="inplace_latest")
    await response.tell(sample_block.update("Message 5"), mode="inplace_latest")

    # - Test inplace by id

    await response.tell("[Test: Inplace by id mode]")

    sample_block = BasicBlock()
    await response.tell(sample_block.update(text="Message 6"))
    sample_block.refresh_id()
    await response.tell(sample_block.update(text="Message 7 - should be updated"), mode="inplace")
    await response.tell(sample_block.update(text="Message 7 - should be updated 2"), mode="inplace")

    await response.tell("Message 8", transient=True)

    await response.tell(sample_block.update(text="Message 7"), mode="inplace")

    # - Test inplace by id with 2 messages

    await response.tell("[Test: Inplace by id with 2 messages]")

    page = Page(
        blocks=[
            BasicBlock(text="Message 10"),
            BasicBlock(text="Message 11 - should be updated"),
        ]
    )

    await response.tell(page)
    page.blocks[0].text = "Message 12"
    page.blocks[0].refresh_id()
    page.blocks[1].text = "Message 11"
    await response.tell(page, mode="inplace")


def test():
    deps = TestDeps.load()
    asyncio.run(
        App().start_polling(
            bot=TestDeps.load().config.telegram_bot_token,
            initial_starters={deps.config.telegram_test_chat_id: starter},
            message_starter=starter,
        )
    )


if __name__ == "__main__":
    test()
