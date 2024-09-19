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


@dataclass
class AppState:
    users: list[User] = field(default_factory=list)


class App:
    def __init__(self):
        self.users: list[User] = []

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
