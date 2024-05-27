from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class ModularClassInterface:
    foo: str

    @abstractmethod
    def some_method(self) -> str:
        pass
