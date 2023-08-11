import re
import unicodedata


def slugify(value, allow_unicode=False):
    """
    Taken from here: https://github.com/django/django/blob/main/django/utils/text.py (2023-08-10)

    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def test():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("Привет, Мир!") == ""
    assert slugify("Привет, Мир!", allow_unicode=True) == "привет-мир"


if __name__ == "__main__":
    test()
