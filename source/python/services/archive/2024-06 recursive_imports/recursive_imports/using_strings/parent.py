from dataclasses import dataclass

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from recursive_imports.using_strings.child import Child


@dataclass
class Parent:
    child: Optional["Child"] = None