from dataclasses import dataclass, field

from palette.teledo.context.interaction import Interaction


@dataclass
class UserContext:
    # - Interactions

    # todo later: index properly [@marklidenberg]
    interactions: list[Interaction]


@dataclass
class Context:
    user_contexts: dict[str, UserContext] = field(default_factory=dict)
    callbacks: dict = field(default_factory=dict)


context = Context()
