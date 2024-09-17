import asyncio

from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    # - Test text messages

    await response.tell("I will ask you some questions")
    age = await response.ask("How old are you?")
    name = await response.ask("What is your name?", update_mode="inplace")
    await response.tell(f"Hello, {name}! You are {age} years old :)")

    # - Test reply keyboard

    button_clicked = await response.ask("Click any button:", reply_keyboard_markup=[["A", "B"], ["C", "D", "E"]])

    await response.tell(f"You clicked {button_clicked}")

    # - Test inline keyboard

    button_clicked = await response.ask(
        "Click any inline button:", inline_keyboard_markup=[["A", "B"], ["C", "D", "E"]]
    )

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
