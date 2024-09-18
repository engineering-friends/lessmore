import asyncio

from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    pass


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
