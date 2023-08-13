import requests

from pymaybe import maybe


def get_shortened_url(url: str) -> str:
    return maybe(requests.get(f"https://tinyurl.com/api-create.php?url={url}").text).or_else("")


def test():
    print(get_shortened_url("https://yandex.ru"))


if __name__ == "__main__":
    test()
