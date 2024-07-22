from dataclasses import (
    dataclass,
    field as dataclass_field,
)
from typing import Optional

from lessmore.utils.functional.dict.drop import drop


@dataclass
class Column:
    attribute: Optional[str] = None
    alias: Optional[str] = None
    is_auto: bool = False

    @property
    def name(self):
        return self.alias or self.attribute


def column(alias: Optional[str] = None, **kwargs):
    # syntax sugar to add field with adding column name to metadata
    return dataclass_field(
        **drop(kwargs, ["metadata"]),
        metadata={
            "column": Column(alias=alias),
            **kwargs.get("metadata", {}),
        },
    )
