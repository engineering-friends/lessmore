from dataclasses import dataclass
from typing import Callable

from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage


"""
- A
- B
- Quit

- A.1
- A.2
- Back
- Cancel

- B.1
- B.2
- Back
- Cancel

"""


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


back = Button(text="Back", callback=lambda response: response.ask(response.previous))
cancel = Button(text="Cancel", callback=lambda response: response.ask(response.root))
quit = Button(text="Quit", callback=lambda response: print("Quitting..."))


starter = lambda response: response.ask(
    Menu(
        [
            Button(
                text="A",
                callback=lambda response: response.ask(
                    page=Menu(
                        buttons=[
                            Button(
                                text="A.1", callback=lambda response: (print("A.1"), response.ask(page=response.root))
                            ),
                            Button(
                                text="A.2", callback=lambda response: (print("A.2"), response.ask(page=response.root))
                            ),
                            back,
                            cancel,
                        ]
                    ),
                    update_mode="inplace",
                ),
            ),
            Button(
                text="B",
                callback=lambda response: response.ask(
                    page=Menu(
                        buttons=[
                            Button(
                                text="B.1", callback=lambda response: (print("B.1"), response.ask(page=response.root))
                            ),
                            Button(
                                text="B.2", callback=lambda response: (print("B.2"), response.ask(page=response.root))
                            ),
                            back,
                            cancel,
                        ]
                    ),
                    update_mode="inplace",
                ),
            ),
            quit,
        ]
    )
)
