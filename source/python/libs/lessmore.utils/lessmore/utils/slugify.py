import re
import unicodedata

from typing import Any


def slugify(value: Any, allow_unicode: bool = False) -> str:
    """
    Taken from here: https://github.com/django/django/blob/main/django/utils/text.py (2023-08-10)

    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """

    # - Convert to string

    value = str(value)

    # - Normalize

    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")

    # - Slugify

    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def test():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("Привет, Мир!") == ""
    assert slugify("Привет, Мир!", allow_unicode=True) == "привет-мир"


if __name__ == "__main__":
    test()
