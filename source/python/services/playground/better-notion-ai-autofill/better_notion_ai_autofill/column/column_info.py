from dataclasses import dataclass
from typing import Optional


@dataclass
class ColumnInfo:
    attribute: Optional[str] = None
    alias: Optional[str] = None
    is_auto: bool = False

    @property
    def name(self):
        return self.alias or self.attribute
