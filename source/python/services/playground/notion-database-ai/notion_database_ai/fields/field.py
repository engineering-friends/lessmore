from dataclasses import field as dataclass_field

from lessmore.utils.functional.dict.drop import drop


def field(name: str, **kwargs):
    # syntax sugar to add field with adding column name to metadata
    return dataclass_field(
        **drop(kwargs, ["metadata"]),
        metadata={
            "property_name": name,
            **kwargs.get("metadata", {}),
        },
    )
