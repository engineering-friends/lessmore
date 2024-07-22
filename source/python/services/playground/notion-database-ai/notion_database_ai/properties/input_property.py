from dataclasses import field

from lessmore.utils.functional.dict.drop import drop


def input_property(name: str, **kwargs):
    # syntax sugar to add field with adding column name to metadata
    return field(
        **drop(kwargs, ["metadata"]),
        metadata={
            "property_name": name,
            **kwargs.get("metadata", {}),
        },
    )
