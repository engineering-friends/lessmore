from collections import defaultdict


class recursive_defaultdict(defaultdict):
    def __init__(self, separator=".", *args, **kwargs):
        self.separator = separator
        super().__init__(lambda: recursive_defaultdict(separator=separator), *args, **kwargs)

    def to_dict(self, recursive=True):
        if recursive:
            return self._to_dict_recursively(self)
        else:
            return dict(self)

    @staticmethod
    def _to_dict_recursively(value):
        if isinstance(value, recursive_defaultdict):
            return {k: recursive_defaultdict._to_dict_recursively(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [recursive_defaultdict._to_dict_recursively(v) for v in value]
        else:
            return value

    def set_dotted(self, key, value):
        # - Init current value

        current_value = self

        # - Create nested sub dictionaries or lists of primitive types
        current_key = key.split(self.separator)[0]
        last_key = key.split(self.separator)[-1]

        for next_key in key.split(self.separator)[1:]:
            _is_current_list_not_setted = isinstance(current_value, list) and int(current_key) not in [
                index for index, _ in enumerate(current_value)
            ]

            if next_key.isnumeric():
                if _is_current_list_not_setted:
                    current_value.insert(int(current_key), [])
                elif not isinstance(current_value, list):
                    current_value.setdefault(current_key, [])
            elif _is_current_list_not_setted:
                current_value.insert(int(current_key), recursive_defaultdict())
            elif not isinstance(current_value, list):
                current_value.setdefault(current_key, recursive_defaultdict())

            current_value = current_value[int(current_key) if current_key.isnumeric() else current_key]
            current_key = next_key

        # - Set value
        if last_key.isnumeric():
            current_value.insert(int(last_key), value)
        else:
            current_value[last_key] = value


def test():
    #   ge grault garply waldo fred plugh xyzzy thud

    value = recursive_defaultdict()
    """
    {
        "foo": {
            "bar": 1
        }
    }
    """
    value.set_dotted("foo.bar", 1)
    # ---

    """
    {
        "bar": {
            "baz": [
                {
                    "qux": "any string"
                } 
            ]
        }
    }
    """
    value.set_dotted("bar.baz.0.qux", "any string")
    # ---

    """
    {
        "cor": {
            "gra": [
                [
                    "list_in_list"
                ],
                [
                    1, 2, 3
                ]
            ]
        }
    }
    """
    value.set_dotted("cor.gra.0.0", "string_element_of_list")
    value.set_dotted("cor.gra.1.0", 1)
    value.set_dotted("cor.gra.1.1", 2)
    value.set_dotted("cor.gra.1.2", 3)
    # ---

    assert value.to_dict() == {
        "foo": {"bar": 1},
        "bar": {"baz": [{"qux": "any string"}]},
        "cor": {"gra": [["string_element_of_list"], [1, 2, 3]]},
    }


if __name__ == "__main__":
    test()
