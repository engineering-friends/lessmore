import asyncio

from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    await response.ask(
        "Test on response",
        inline_keyboard=[["✅ Да", "❌ Нет"]],
        on_response=lambda response: response.tell("On response"),
    )


def test():
    deps = TestDeps.load()
    asyncio.run(
        App().run(
            bot=TestDeps.load().config.telegram_bot_token,
            starters={deps.config.telegram_test_chat_id: starter},
            message_starter=starter,
        )
    )


if __name__ == "__main__":
    test()
