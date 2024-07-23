from dataclasses import (
    field as dataclass_field,
)
from typing import Optional

from lessmore.utils.functional.dict.drop import drop

from better_notion_ai_autofill.column.column_info import ColumnInfo


def column(alias: Optional[str] = None, **kwargs):
    # syntax sugar to add field with adding column name to metadata
    return dataclass_field(
        **drop(kwargs, ["metadata"]),
        metadata={
            "column_info": ColumnInfo(alias=alias),
            **kwargs.get("metadata", {}),
        },
    )
