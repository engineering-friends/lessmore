import asyncio

from aiogram.types import ReplyKeyboardRemove
from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
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
    )  # have to remove the keyboard with a separate message

    # - Test inline keyboard

    button_clicked = await response.ask("Click any inline button:", inline_keyboard=[["A", "B"], ["C", "D", "E"]])

    await response.tell(f"You clicked {button_clicked}")


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
