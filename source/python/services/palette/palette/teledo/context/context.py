from dataclasses import dataclass, field

from palette.teledo.context.user_context import UserContext


@dataclass
class Context:
    user_contexts: dict[str, UserContext] = field(default_factory=dict)
    callbacks: dict = field(default_factory=dict)


context = Context()
