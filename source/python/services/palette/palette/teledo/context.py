import asyncio

from asyncio import Future
from dataclasses import dataclass, field


@dataclass
class Context:
    thread_messages: list = field(default_factory=list)
    callbacks: dict = field(default_factory=dict)
    telegram_interaction: Future = field(default_factory=asyncio.Future)
