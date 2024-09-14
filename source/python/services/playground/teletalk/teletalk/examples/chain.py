from dataclasses import dataclass
from typing import Callable


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
class Button:
    text: str
    callback: Callable


class Menu:
    def __init__(self, buttons: list[Button]):
        self.buttons = buttons


back = Button(text="Back", callback=lambda response: response.ask(response.previous))
cancel = Button(text="Cancel", callback=lambda response: response.ask(response.root))
quit = Button(text="Quit", callback=lambda response: ...)

starter = lambda response: response.ask(
    Menu(
        [
            Button(
                text="A",
                callback=lambda response: Menu(
                    buttons=[
                        Button(text="A.1", callback=lambda response: (print("A.1"), response.ask(response.root))),
                        Button(text="A.2", callback=lambda response: (print("A.2"), response.ask(response.root))),
                        back,
                        cancel,
                    ]
                ),
            ),
            Button(
                text="B",
                callback=lambda response: Menu(
                    buttons=[
                        Button(text="B.1", callback=lambda response: (print("B.1"), response.ask(response.root))),
                        Button(text="B.2", callback=lambda response: (print("B.2"), response.ask(response.root))),
                        back,
                        cancel,
                    ]
                ),
            ),
            quit,
        ]
    )
)
