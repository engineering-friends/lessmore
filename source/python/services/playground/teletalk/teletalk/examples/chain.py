import asyncio

from teletalk.app import App
from teletalk.models.response import Response


async def starter(response: Response):
    await response.tell(text="I will ask you some questions")
    age = await response.ask(text="How old are you?")
    name = await response.ask(text="What is your name?")
    await response.tell(text=f"Hello, {name}! You are {age} years old.")


def test():
    asyncio.run(App(bot=Deps.load().config.telegram_bot_token, message_starter=echo).start_polling())
