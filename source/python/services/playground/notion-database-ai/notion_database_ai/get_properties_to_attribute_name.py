import inspect

from dataclasses import dataclass
from typing import Any

from notion_database_ai.fields.auto_field import auto_property
from notion_database_ai.fields.input_property import input_property


def get_property_name_to_attribute_name(row: Any) -> dict:
    # - Get column_name_by_attribute_name

    property_name_to_attribute_name = {}

    # -- Go through fields first

    for field_name, field in row.__dataclass_fields__.items():
        if "property_name" in field.metadata:
            property_name_to_attribute_name[field.metadata["property_name"]] = field_name
        else:
            property_name_to_attribute_name[field_name] = field_name

    # -- Go through all auto_properties

    # --- Collect auto properties

    for attr_name in dir(row):
        attr = getattr(row, attr_name)
        if inspect.isawaitable(attr):
            attr.close()

    # --- Add auto_properties

    property_name_to_attribute_name.update(row.auto_property_name_to_attribute_name)

    return property_name_to_attribute_name


def test():
    @dataclass
    class Example:
        title: str
        my_number: int = input_property(name="My Number")

        @auto_property
        async def name(self):
            return "Example"

        @auto_property(name="Foo")
        async def foo(self):
            return "Foo"

    assert get_property_name_to_attribute_name(Example(title="foo", my_number=123)) == {
        "title": "title",
        "My Number": "my_number",
        "Foo": "foo",
        "name": "name",
    }


if __name__ == "__main__":
    test()
