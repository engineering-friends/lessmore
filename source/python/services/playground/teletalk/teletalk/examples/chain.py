import asyncio

from teletalk.models.response import Response


async def starter(response: Response):
    # - Ask questions
    age = await response.ask(text="How old are you?")
    name = await response.ask(text="What is your name?")
    await response.tell(text=f"Hello, {name}! You are {age} years old.")
