import copy
import re


def resolve_dict_placeholders(dic):
    """Resolve string self-placeholders in a dictionary recursively"""

    # - Copy the dictionary to avoid modifying the original

    dic = copy.deepcopy(dic)

    # - Find placeholders

    placeholder_pattern = re.compile(r"\{\{([^}]+)\}\}")

    # - Resolve placeholders

    def resolve_placeholders(dic: dict, s: str):
        matches = placeholder_pattern.findall(s)
        for match in matches:
            _keys = match.split(".")
            cursor = dic
            for _key in _keys:
                if _key in cursor:
                    cursor = cursor[_key]
                else:
                    raise Exception(f"Key '{_key}' not found in dictionary")

            if isinstance(cursor, str):
                cursor = resolve_placeholders(dic=dic, s=cursor)
            s = s.replace(f"{{{{{match}}}}}", str(cursor))
        return s

    def recursive_resolve(sub_dic: dict, dic: dict):
        for key, value in sub_dic.items():
            if isinstance(value, dict):
                recursive_resolve(sub_dic=value, dic=dic)
            elif isinstance(value, str):
                sub_dic[key] = resolve_placeholders(dic=dic, s=value)

    recursive_resolve(dic, dic)

    return dic


def test():
    assert resolve_dict_placeholders(
        {
            "a": 1,
            "h": "{{b}}",
            "b": "{{a}} and {{c}}",
            "c": "value of c",
            "d": {"e": "nested {{a}}"},
            "f": {"g": "deeply nested {{d.e}}"},
        }
    ) == {
        "a": 1,
        "h": "1 and value of c",
        "b": "1 and value of c",
        "c": "value of c",
        "d": {"e": "nested 1"},
        "f": {"g": "deeply nested nested 1"},
    }


if __name__ == "__main__":
    test()
