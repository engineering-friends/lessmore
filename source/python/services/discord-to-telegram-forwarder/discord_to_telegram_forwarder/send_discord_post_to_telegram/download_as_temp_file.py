import os
import tempfile

import requests

from lessmore.utils.file_primitives.write_file import write_file


def _download_as_temp_file(url: str, extension: str = None) -> str:
    # - Prepare temp file

    filename = tempfile.NamedTemporaryFile(dir="/tmp", delete=False).name

    if extension:
        filename += extension

    # - Download file

    response = requests.get(url, allow_redirects=True)
    write_file(data=response.content, filename=filename, as_bytes=True)

    # - Return

    return filename


def test():
    sample_url = "https://cdn.discordapp.com/attachments/913095424225706005/913095454503211274/unknown.png"
    temp_path = _download_as_temp_file(sample_url)
    assert os.path.isfile(temp_path)


if __name__ == "__main__":
    test()
