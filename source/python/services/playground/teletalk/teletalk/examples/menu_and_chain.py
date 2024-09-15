from dataclasses import dataclass
from typing import Callable

from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response


@dataclass
class Button(Block):
    text: str
    callback: Callable

    def render(self) -> BlockMessage:
        raise NotImplementedError


class Menu(Block):
    def __init__(self, buttons: list[Button]):
        self.buttons = buttons

        super().__init__()

    def render(self) -> BlockMessage:
        raise NotImplementedError


async def chain(response: Response):
    # - Update menu in processing mode

    await response.tell(text="Answer the questions...", update_mode="inplace")

    # - Ask questions

    age = await response.ask(text="How old are you?")
    name = await response.ask(text="What is your name?")
    await response.tell(text=f"Hello, {name}! You are {age} years old.")

    # - Go back to the menu, creating a new menu message

    await response.ask(page=response.root)


starter = lambda response: response.ask(Menu([Button(text="Chain", callback=chain)]))
