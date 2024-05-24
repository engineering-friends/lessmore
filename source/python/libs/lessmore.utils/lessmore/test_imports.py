import fnmatch
import glob
import importlib.util
import os
import sys

import tqdm

from loguru import logger

from lessmore.utils.file_primitives.list_files import list_files
from lessmore.utils.loguru_utils.format_as_colored_json.format_as_colored_json import format_as_colored_json
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru


# - Utils


def _import_module(path):
    spec = importlib.util.spec_from_file_location(
        "module.name",
        path,
    )
    foo = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = foo
    spec.loader.exec_module(foo)


# - Test_imports


def test_imports(path):
    # import all files and make sure there is no import errors
    for fn in tqdm.tqdm(
        list_files(
            path,
            pattern=lambda filename: filename.endswith(".py")
            and ".venv" not in filename
            and "__pycache__" not in filename
            and "archive" not in filename,
        )
    ):
        _import_module(fn)


if __name__ == "__main__":
    setup_json_loguru()

    # logger.info('Start testing imports')
    # test_imports('utils/')

    import time

    from tqdm import tqdm

    def process_items(items):
        for item in tqdm(items, desc="Processing items"):
            tqdm.write(f"Current value: {item}")
            time.sleep(0.1)  # Simulate some processing time
            yield item

    def main():
        items = [1, 2, 3, 4, 5]
        for item in process_items(items):
            pass  # Do something with each item if needed

    if __name__ == "__main__":
        main()
