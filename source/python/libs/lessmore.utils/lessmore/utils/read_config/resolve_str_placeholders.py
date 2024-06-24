import re


def resolve_str_placeholders(s: str, context: dict):
    """Resolve string placeholders from the context if possible.
    Try to resolve placeholders in string (e.g. 'foo {bar} baz {qux}', {"bar": 1} -> 'foo 1 baz {qux}')
    """

    def resolve_placeholder(match):
        key = match.group(1)
        return str(context.get(key, match.group(0)))

    return re.sub(r"\{(\w+)\}", resolve_placeholder, s)


def test():
    assert resolve_str_placeholders("foo {bar} baz {qux}", context={"bar": 1}) == "foo 1 baz {qux}"


if __name__ == "__main__":
    test()
