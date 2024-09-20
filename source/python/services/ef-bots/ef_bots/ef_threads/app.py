from dataclasses import asdict, dataclass, field
from pathlib import Path

import dacite

from rocksdict import Rdict


@dataclass
class User:
    id: int
    current_thread_id: int = 0
    thread_ids: list[int] = field(default_factory=list)
    thread_id_by_message_id: dict[int, int] = field(default_factory=dict)


@dataclass
class AppState:
    users: dict[int, User] = field(default_factory=dict)


class App:
    def __init__(self):
        self.users: dict[int, User] = {}
        self.telegram_usernames_by_notion_whois_url: dict[str, str] = {}
        self.last_checked_telegram_username_at_by_notion_whois_url: dict[str, int] = {}

        self.rdict = Rdict(path=str(Path(__file__).parent / "state"))

    def load_state(self):
        self.users = dacite.from_dict(data_class=AppState, data=dict(self.rdict)).users

    def dump_state(self):
        # # - DEPRECATED: Clean up thread_id_by_message_id of the users, as they are large
        #
        # for user in self.users:
        #     last_message_id = max(user.thread_id_by_message_id.keys())
        #     last_thread_id = max(user.thread_id_by_message_id.values())
        #     user.thread_id_by_message_id = {
        #         k: v for k, v in user.thread_id_by_message_id.items() if k >= last_thread_id - 10_000
        #     }

        # - Dump state

        for user in self.users.values():
            self.rdict[user.id] = user

        self.rdict.flush()
