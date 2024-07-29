import requests


def get_shortened_url_from_tiny_url(url: str) -> str:
    try:
        return requests.get(f"https://tinyurl.com/api-create.php?url={url}").text
    except Exception as e:
        return ""


def test():
    print(get_shortened_url_from_tiny_url("https://google.com"))


if __name__ == "__main__":
    test()
