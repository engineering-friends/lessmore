from dataclasses import dataclass, field

from palette.teledo.interaction import Interaction


@dataclass
class Context:
    interactions_by_user_id: dict[str, dict[str, Interaction]] = field(default_factory=dict)
    callbacks: dict = field(default_factory=dict)


context = Context()
