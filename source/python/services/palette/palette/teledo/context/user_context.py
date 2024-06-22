from dataclasses import dataclass, field

from palette.teledo.context.interaction import Interaction


@dataclass
class UserContext:
    # - Interactions
    user_id: int
    # todo later: index properly [@marklidenberg]
    interactions: list[Interaction] = field(default_factory=list)
    active_question_message_ids: list[str] = field(default_factory=list)


@dataclass
class Context:
    user_contexts: dict[str, UserContext] = field(default_factory=dict)
    callbacks: dict = field(default_factory=dict)
