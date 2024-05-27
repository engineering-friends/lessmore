import fnmatch
import glob
import importlib.util
import os
import sys

import tqdm

from loguru import logger

from lessmore.utils.file_primitives.list_files import list_files
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.track import track


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
    for fn in track(
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

    test_imports("discord_to_telegram_forwarder/")
