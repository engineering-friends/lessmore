import asyncio

from asyncio import Future
from dataclasses import dataclass, field


@dataclass
class Context:
    thread_messages: list = field(default_factory=list)
    callbacks_infos: dict = field(default_factory=dict)
    callback_id_future: Future = field(default_factory=asyncio.Future)


context = Context()
