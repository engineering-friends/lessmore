import json
import os.path

from dataclasses import asdict, dataclass, field

import dacite

from lessmore.utils.file_primitives.read_file import read_file

from deeplay.utils.file_utils.write_file import write_file


@dataclass
class User:
    id: int
    current_thread_id: int = 0
    thread_ids: list[int] = field(default_factory=list)
    first_thread_message_id: int = 0


@dataclass
class AppState:
    users: list[User] = field(default_factory=list)

    telegram_usernames_by_notion_whois_url: dict[str, str] = field(default_factory=dict)
    last_checked_telegram_username_at_by_notion_whois_url: dict[str, int] = field(default_factory=dict)


class App:
    def __init__(self):
        self.users: list[User] = []
        self.telegram_usernames_by_notion_whois_url: dict[str, str] = {}
        self.last_checked_telegram_username_at_by_notion_whois_url: dict[str, int] = {}

    def load_state(self):
        state_dict = read_file(os.path.join(os.path.dirname(__file__), "state.json"), reader=json.load, default={})
        state = dacite.from_dict(AppState, state_dict)
        self.users = state.users

    def dump_state(self):
        write_file(
            data=asdict(AppState(users=self.users)),
            filename=os.path.join(os.path.dirname(__file__), "state.json"),
            writer=json.dump,
        )

    @property
    def users_by_id(self):
        return {user.id: user for user in self.users}