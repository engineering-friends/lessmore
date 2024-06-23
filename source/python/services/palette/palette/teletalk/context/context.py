from dataclasses import dataclass, field

from palette.teletalk.context.user_context import Talker


@dataclass
class Context:
    user_contexts: dict[int, Talker] = field(default_factory=dict)

    def get_user_context(self, user_id: int) -> Talker:
        return self.user_contexts.setdefault(user_id, Talker(user_id=user_id))


context = Context()
