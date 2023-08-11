from abc import abstractmethod
from typing import Dict


class TransactionManager:
    @abstractmethod
    def get_status(self, id: str):
        raise NotImplementedError()

    @abstractmethod
    def is_submitted(self, id: str):
        raise NotImplementedError()

    @abstractmethod
    def submit(self, id: str, status: str, body: str = ""):
        raise NotImplementedError()

    @abstractmethod
    def reset(self):
        raise NotImplementedError()

    @abstractmethod
    def get_all(self) -> Dict:  # {<status>: <paths>}
        raise NotImplementedError()
