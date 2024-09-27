"""Test imports of all files in the utils folder."""

import fnmatch
import glob
import importlib.util
import os
import sys

from lessmore.utils.file_primitives.list_files import list_files
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.track import track
from loguru import logger


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
    logger.info("Start testing imports")
    test_imports("ef_bots/")
