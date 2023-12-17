import os

import requests


def _download_as_temp_file(url, filename):
    r = requests.get(url, allow_redirects=True)
    temp_path = "/tmp/discord_to_telegram_forwarder/" + filename
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "wb") as temp_file:
        temp_file.write(r.content)
    return temp_path


def test():
    sample_url = "https://cdn.discordapp.com/attachments/913095424225706005/913095454503211274/unknown.png"
    sample_filename = "unknown.png"
    temp_path = _download_as_temp_file(sample_url, sample_filename)
    print(temp_path)
    assert os.path.isfile(temp_path)
    os.remove(temp_path)


if __name__ == "__main__":
    test()
