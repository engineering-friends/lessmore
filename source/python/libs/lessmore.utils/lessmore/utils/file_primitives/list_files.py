import fnmatch
import os

from functools import partial
from typing import Callable, Union


def list_files(
    path: str,
    pattern: Union[None, str, Callable] = None,
    recursive: bool = True,
):
    # - Get list of files

    if not recursive:
        filenames = [filename for filename in os.listdir(path) if os.path.isfile(filename)]
    else:
        if os.path.isfile(path):
            filenames = [path]
        else:
            # glob.glob('**/*') is slower 2.5 times than simple os.walk. It also returns directories
            filenames = []
            for root, dirs, files in os.walk(path):
                filenames += [os.path.join(root, filename) for filename in files]

    # - Set filter for string pattern

    if isinstance(pattern, str):
        pattern = partial(fnmatch.fnmatch, pat=pattern)

    # - Filter

    if pattern:
        filenames = [filename for filename in filenames if pattern(filename)]

    # - Return

    return filenames


def test():
    print(
        list_files(
            "..",
            pattern="*",
            recursive=True,
        )
    )


if __name__ == "__main__":
    test()
