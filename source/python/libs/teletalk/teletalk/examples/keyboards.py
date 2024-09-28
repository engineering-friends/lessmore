import asyncio

from aiogram.types import (
    KeyboardButton,
    KeyboardButtonPollType,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUser,
    KeyboardButtonRequestUsers,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from loguru import logger
from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def custom_messages(response: Response):
    # - Test text messages

    message = await response.ask(
        "Send me your location",
        keyboard=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Send contact", request_contact=True)],
                [KeyboardButton(text="Send location", request_location=True)],
                [KeyboardButton(text="Send poll", request_poll=KeyboardButtonPollType(type="quiz"))],
                # todo later: add more keyboard buttons [@marklidenberg]
                # [KeyboardButton(text="Request users", request_users=KeyboardButtonRequestUsers(request_id=0, user_is_premium=True))],
                # [KeyboardButton(text="Request user", request_user=KeyboardButtonRequestUser(request_id=0, user_is_premium=True))],
                # [KeyboardButton(text="Send chat", request_chat=KeyboardButtonRequestChat(request_id=0, chat_is_channel=True))],
                # [KeyboardButton(text="Web app", web_app=None)],
            ]
        ),
        one_time_keyboard=False,
        message_callback=lambda response: response.message,
    )

    logger.debug("Message", contact=message.contact, location=message.location, text=message.text)


def test():
    deps = TestDeps.load()
    asyncio.run(
        App().run(
            bot=deps.config.telegram_bot_token,
            starters={deps.config.telegram_test_chat_id: custom_messages},
            message_starter=custom_messages,
        )
    )


if __name__ == "__main__":
    test()
