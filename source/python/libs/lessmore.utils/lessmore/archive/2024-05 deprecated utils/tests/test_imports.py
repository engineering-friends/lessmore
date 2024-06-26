import fnmatch
import glob
import importlib.util
import os
import sys

from loguru import logger


# - Utils


def _list_files(path, pattern=None, recursive=True):
    # todo later: put to utils [@marklidenberg]
    if not recursive:
        fns = os.listdir(path)
    else:
        # glob.glob('**/*') is slower 2.5 times than simple os.walk. It also returns directories
        fns = []
        for root, dirs, files in os.walk(path):
            # todo later: make os.path.join faster? [@marklidenberg]
            fns += [os.path.join(root, fn) for fn in files]
    if pattern:
        fns = [fn for fn in fns if fnmatch.fnmatch(fn, pattern)]
    return fns


def _import_module(path):
    spec = importlib.util.spec_from_file_location(
        "module.name",
        path,
    )
    foo = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = foo
    spec.loader.exec_module(foo)


# - Test_imports


def run_imports_test(path):
    from lessmore.utils.loguru_utils import setup_json_loguru

    configure_loguru("debug")

    # import all files and make sure there is no import errors
    for fn in _list_files(path, pattern="*.py"):
        if ".venv" in fn or "__pycache__" in fn and "/archive/" not in fn:
            continue
        logger.debug("Importing file", fn=fn)

        try:
            _import_module(fn)
        except:
            logger.exception("Failed", fn=fn)
