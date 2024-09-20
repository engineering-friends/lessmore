import asyncio

from functools import partial

from aiogram.types import ReplyKeyboardRemove
from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response, chat_id: int = 0):
    # - Set chat id
    if chat_id:
        response.chat_id = chat_id

    # - Test text messages

    await response.tell("I will ask you some questions")
    age = await response.ask("How old are you?")
    name = await response.ask("What is your name?", mode="inplace")
    await response.tell(f"Hello, {name}! You are {age} years old :)")

    # - Test reply keyboard

    button_clicked = await response.ask(
        "Click any button:", keyboard=[["A", "B"], ["C", "D", "E"]], one_time_keyboard=False
    )

    await response.tell(f"You clicked {button_clicked}")

    button_clicked = await response.ask("Click any button:")  # note: the keyboard is still present

    await response.tell(f"You clicked {button_clicked}")

    await response.tell(
        "Remove keyboard", keyboard=ReplyKeyboardRemove()
    )  # have to remove the keyboard with a separate message, can't be inline message, as only one markup is allowed

    # - Test inline keyboard

    button_clicked = await response.ask("Click any inline button:", inline_keyboard=[["A", "B"], ["C", "D", "E"]])

    await response.tell(f"You clicked {button_clicked}")


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
