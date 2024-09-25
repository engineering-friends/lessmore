import asyncio

from teletalk.app import App
from teletalk.blocks.mark_text_with_inline_response import mark_text_with_inline_response
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    await response.ask(
        "Test on response", inline_keyboard=[["✅ Да", "❌ Нет"]], on_response=mark_text_with_inline_response
    )


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
