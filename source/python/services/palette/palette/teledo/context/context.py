from dataclasses import dataclass, field
from typing import Optional

from aiogram import Bot, Dispatcher

from palette.teledo.context.user_context import UserContext


@dataclass
class Context:
    bot: Optional[Bot] = None
    user_contexts: dict[int, UserContext] = field(default_factory=dict)

    def get_user_context(self, user_id: int) -> UserContext:
        return self.user_contexts.setdefault(user_id, UserContext(user_id=user_id))


context = Context()
