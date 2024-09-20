import asyncio

from functools import partial

from teletalk.app import App
from teletalk.models.page import Page
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response, chat_id: int = 0):
    if chat_id:
        response.chat_id = chat_id

    await response.tell("Message 1", mode="create_new")
    await response.tell("Message 2", mode="create_new")
    await asyncio.sleep(1)

    await response.purge_talk()


def test():
    deps = TestDeps.load()
    asyncio.run(
        App(
            bot=deps.config.telegram_bot_token,
            initial_starters=[partial(starter, chat_id=deps.config.telegram_test_chat_id)],
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
