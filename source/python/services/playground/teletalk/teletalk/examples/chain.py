import asyncio

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram import ReplyKeyboardMarkup
from teletalk.app import App
from teletalk.models.block import Block, persist
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    # - Test text messages

    await response.tell(text="I will ask you some questions")
    age = await response.ask(text="How old are you?")
    name = await response.ask(text="What is your name?", update_mode="inplace")
    await response.tell(text=f"Hello, {name}! You are {age} years old :)")

    # - Test reply keyboard

    button_clicked = await response.ask(
        text="Click any button",
        reply_keyboard_markup=[["A", "B"], ["C", "D", "E"]],
    )

    await response.tell(text=f"You clicked {button_clicked}")

    # - Test inline keyboard

    button_clicked = await response.ask(
        text="Click any button",
        inline_keyboard_markup=[["A", "B"], ["C", "D", "E"]],
    )

    await response.tell(text=f"You clicked {button_clicked}")


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
