from dataclasses import dataclass
from typing import Callable

from teletalk.models.response import Response


@dataclass
class Button:
    text: str
    callback: Callable


class Menu:
    def __init__(self, buttons: list[Button]):
        self.buttons = buttons


async def a(response: Response):
    # - Update menu in processing mode

    await response.tell(text="Answer the questions...", update_mode="inplace")

    # - Ask questions

    age = await response.ask(text="How old are you?")
    name = await response.ask(text="What is your name?")
    await response.tell(text=f"Hello, {name}! You are {age} years old.")

    # - Go back to the menu, creating a new menu message

    await response.ask(response.root)


starter = lambda response: response.ask(Menu([Button(text="A", callback=a)]))
