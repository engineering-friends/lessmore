import asyncio

from teletalk.app import App
from teletalk.models.page import Page
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    # - Test text messages

    await response.tell("Message 1", mode="create_new")
    await response.tell("Message 2", mode="create_new")
    await asyncio.sleep(1)

    await response.purge_talk()


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
