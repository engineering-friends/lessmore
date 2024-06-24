from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from recursive_imports.using_strings.parent import Parent


@dataclass
class Child:
    parent: "Parent"