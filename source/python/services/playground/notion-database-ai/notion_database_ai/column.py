from dataclasses import field

from lessmore.utils.functional.dict.drop import drop


def column(name: str, **kwargs):
    # syntax sugar to add field with adding column name to metadata
    return field(
        **drop(kwargs, ["metadata"]),
        metadata={
            "column_name": name,
            **kwargs.get("metadata", {}),
        },
    )
