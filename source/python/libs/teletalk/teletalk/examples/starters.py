import asyncio

from aiogram.types import ReplyKeyboardRemove
from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


def test():
    deps = TestDeps.load()

    asyncio.run(
        App().start_polling(
            bot=deps.config.telegram_bot_token,
            initial_starters={deps.config.telegram_test_chat_id: lambda response: response.tell("Initial starter")},
            message_starter=lambda response: response.tell("Message starter"),
            command_starters={"/start": lambda response: response.tell("Command starter")},
        )
    )


if __name__ == "__main__":
    test()
