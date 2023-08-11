from pymaybe import maybe


assert maybe("I'm a value").is_some()

assert not maybe("I'm a value").is_none()

assert not maybe(None).is_some()

assert maybe(None).is_none()

assert maybe("I'm a value").get() == "I'm a value"

assert maybe("I'm a value").or_else(lambda: "No value") == "I'm a value"

try:
    maybe(None).get()
except Exception as e:
    assert str(e) == "No such element"

assert maybe(None).or_else(None) is None

assert maybe(None).or_else(lambda: "value") == "value"

assert maybe(None).or_else("value") == "value"


nested_dict = {"a": {"b": {"c": "value"}}}

assert maybe(nested_dict)["a"]["b"]["c"].or_else(None) == "value"
assert maybe(nested_dict)["a"]["b"]["c"]["d"].or_else(None) is None
