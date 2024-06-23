from dataclasses import dataclass, field

from palette.teletalk.crowd.chat import Chat


@dataclass
class Crowd:
    chats: dict[int, Chat] = field(default_factory=dict)

    def get_chat(self, user_id: int) -> Chat:
        return self.chats.setdefault(user_id, Chat())


crowd = Crowd()
