import asyncio

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Interaction:
    id: str = ""
    user_id: str = ""
    ask_message_id: str = ""  # message id of the message that asked the question
    ui_callback_id_future: Optional[asyncio.Future] = field(
        default_factory=lambda: asyncio.get_running_loop().create_future()
    )  # this future is set when global query_handler is called with appropriate callback_id
    state: dict = field(default_factory=dict)

    @property
    def is_active(self):
        return self.ask_message_id != ""
