from dataclasses import dataclass, field

from palette.teletalk.crowd.talker import Talker


@dataclass
class Crowd:
    talkers: dict[int, Talker] = field(default_factory=dict)

    def get_talker(self, user_id: int) -> Talker:
        return self.talkers.setdefault(user_id, Talker())


crowd = Crowd()
