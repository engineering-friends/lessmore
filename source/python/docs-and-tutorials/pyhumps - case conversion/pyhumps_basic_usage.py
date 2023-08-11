import humps


# - Basic: snake_case <-> pascalCase <-> camelCase

# snake_case -> *
assert humps.is_snakecase("foo_bar")
assert humps.camelize("foo_bar") == "fooBar"
assert humps.pascalize("foo_bar") == "FooBar"

# camelCase -> *
assert humps.is_camelcase("fooBar")
assert humps.decamelize("fooBar") == "foo_bar"
assert humps.pascalize("fooBar") == "FooBar"

# pascalCase -> *
assert humps.is_pascalcase("FooBar")
assert humps.depascalize("FooBar") == "foo_bar"
assert humps.camelize("FooBar") == "fooBar"

# - Kebab

assert humps.kebabize("foo_bar") == "foo-bar"
assert humps.dekebabize("foo-bar") == "foo_bar"
assert humps.is_kebabcase("foo-bar")
assert humps.dekebabize("FOO-Bar-baz") == "FOO_Bar_baz"
