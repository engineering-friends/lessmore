import asyncio

from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    # - Test create_new and inplace modes

    ...


def test():
    asyncio.run(
        App().start_polling(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        )
    )


if __name__ == "__main__":
    test()
