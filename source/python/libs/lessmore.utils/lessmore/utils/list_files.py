import fnmatch
import os

from functools import partial
from typing import Callable, Union


def list_files(
    path,
    filter_pattern: Union[None, str, Callable[[str], bool]] = "*",
    recursive=True,
):
    # - Get list of files

    if not recursive:
        filenames = os.listdir(path)
        filenames = [filename for filename in filenames if os.path.isfile(filename)]
    else:
        if os.path.isfile(path):
            filenames = [path]
        else:
            # glob.glob('**/*') is slower 2.5 times than simple os.walk. It also returns directories
            filenames = []
            for root, dirs, files in os.walk(path):
                filenames += [os.path.join(root, filename) for filename in files]

    # - Set filter for string pattern

    if isinstance(filter_pattern, str):
        filter_pattern = partial(fnmatch.fnmatch, pat=filter_pattern)

    # - Filter

    if filter_pattern:
        filenames = [filename for filename in filenames if filter_pattern(filename)]
    return filenames


def test():
    print(
        list_files(
            ".",
            filter_pattern="*",
            recursive=True,
        )
    )


if __name__ == "__main__":
    test()
