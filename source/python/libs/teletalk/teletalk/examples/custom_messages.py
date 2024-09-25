import asyncio

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def custom_messages(response: Response):
    # - Test text messages

    age = await response.ask(
        "Send me your location",
        keyboard=[["A", "B"], ["C", "D", "E"]],
        one_time_keyboard=False,
    )


def test():
    deps = TestDeps.load()
    asyncio.run(
        App(
            bot=deps.config.telegram_bot_token,
            initial_starters={deps.config.telegram_test_chat_id: custom_messages},
            message_starter=custom_messages,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
