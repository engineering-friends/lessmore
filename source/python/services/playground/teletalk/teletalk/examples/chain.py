import asyncio

from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    await response.tell(text="I will ask you some questions")
    age = await response.ask(text="How old are you?")
    name = await response.ask(text="What is your name?")
    await response.tell(text=f"Hello, {name}! You are {age} years old :)")


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
