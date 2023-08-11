import glob
import os.path

from loguru import logger

from lessmore.utils.list_files import list_files
from lessmore.utils.optimize_imports.functions.get_init_py_filenames import get_init_py_filenames


def update_init_py_imports(dir):
    for init_py_path in sorted(
        get_init_py_filenames(dir), key=len, reverse=True
    ):  # go from deepest to shallowest so that all __init__.py would be initialized in and filled later to parent __init__.py file
        # - Get content of old __init__.py file

        if os.path.exists(init_py_path):
            with open(init_py_path, "r") as f:
                old_content = f.read()
        else:
            old_content = ""

        # - Get modules under __init__.py directory (.py files and directories with __init__.py)

        module_paths = glob.glob(
            f"{init_py_path[:-len('__init__.py')]}*"
        )  # pattern_pipeline/__init__.py -> pattern_pipeline/*

        # remove system paths
        module_paths = [module_path for module_path in module_paths if os.path.basename(module_path)[0] != "_"]

        # select modules
        module_paths = [
            module_path
            for module_path in module_paths
            if os.path.splitext(module_path)[1] == ".py" or os.path.exists(f"{module_path}/__init__.py")
        ]

        # sort
        module_paths = sorted(module_paths)

        # - Create new content

        new_content = ""
        for module_path in module_paths:
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            new_content += f"from .{module_name} import *\n"

        if old_content == new_content:
            continue

        # - Write new __init__.py

        with open(init_py_path, "w") as f:
            f.write(new_content)

        logger.info("Updated", path=init_py_path)


def test():
    from lessmore.utils.loguru_utils import configure_loguru

    configure_loguru(level="DEBUG")

    # - Remove __init__.py files

    for init_py_path in list_files(
        os.path.join(os.path.dirname(__file__), "../test/my_module"), filter_pattern="*__init__.py"
    ):
        logger.info("Removing for test", path=init_py_path)
        os.remove(init_py_path)

    # - Update __init__.py files

    update_init_py_imports(os.path.join(os.path.dirname(__file__), "../test/"))


if __name__ == "__main__":
    test()
