import asyncio

from aiogram.types import ReplyKeyboardRemove
from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


# todo later: add example
def test():
    deps = TestDeps.load()

    asyncio.run(App().start_polling(bot=deps.config.telegram_bot_token))


if __name__ == "__main__":
    test()
