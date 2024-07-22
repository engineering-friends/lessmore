from dataclasses import field as dataclass_field
from typing import Optional

from lessmore.utils.functional.dict.drop import drop


def column(alias: Optional[str] = None, **kwargs):
    # syntax sugar to add field with adding column name to metadata
    return dataclass_field(
        **drop(kwargs, ["metadata"]),
        metadata={
            "column": {
                "alias": alias,
                "is_auto": False,
            },
            **kwargs.get("metadata", {}),
        },
    )
