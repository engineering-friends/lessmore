import os.path
import re

from loguru import logger

from lessmore.utils.file_primitives.list_files import list_files
from lessmore.utils.modular_code.modular_class._build_class_file_content import _build_class_file_content
from lessmore.utils.modular_code.modular_class._get_caller_filename import _get_caller_filename
from lessmore.utils.modular_code.modular_class._get_self_functions_from_module._get_self_functions_from_module import (
    _get_self_functions_from_module,
)


def update_modular_class_inline() -> None:
    """
    Updates inline modular class file. It finds all class-like functions (functions with self as first argument) in the same directory as the class file and adds them to the class.

    See example in example/modular_class.py

    """
    # - Get path from where the function is called

    caller_filename = _get_caller_filename()  # example/modular_class.py

    with open(caller_filename) as f:
        caller_file_content = f.read()

    caller_dirname = os.path.dirname(caller_filename)  # example

    # - Find class name

    class_name = re.search(r"class (\w+)\(", caller_file_content).group(1)  # ModularClass

    # - Iterate over files in the directory and collect all functions

    python_filenames = list_files(path=caller_dirname, pattern="*.py")

    # filter caller_filename
    python_filenames = [
        python_filename for python_filename in python_filenames if python_filename != caller_filename
    ]  # ["example/some_method.py", "example/modular_class_data.py", "example/test_modular_class.py"]

    # - Get class_module_path (deeplay.utils.modular_code.modular_class.example) by finding data class import statement

    class_module_path = None
    for line in caller_file_content.splitlines():
        if "from " in line and f"import {class_name}Data" in line:
            # assert line == "from lessmore.utils.modular_code.modular_class.example.modular_class_data import ModularClassData"
            class_module_path = line.split("from ")[1].split(" import ")[
                0
            ]  # deeplay.utils.modular_code.modular_class.example.modular_class_data
            break
    class_module_path = class_module_path.rsplit(".", 1)[0]  # deeplay.utils.modular_code.modular_class.example

    if not class_module_path:
        raise ValueError(f"Could not find import statement for {class_name}Data")

    # - Get self functions from python_filenames

    self_function_to_its_filename = {}
    for python_filename in python_filenames:
        for func in _get_self_functions_from_module(python_filename):
            self_function_to_its_filename[func] = python_filename

    # - Create code for the class file

    code = _build_class_file_content(
        class_name=class_name,
        class_module_path=class_module_path,
        function_to_its_filename=self_function_to_its_filename,
        extra_import_lines=[
            line for line in caller_file_content.splitlines() if "import update_modular_class_inline" in line
        ],
    )

    # - Write code to file

    logger.debug("Writing code to file", caller_filename=caller_filename, code=code)

    with open(caller_filename + ".tmp", "w") as f:
        f.write(code)
    os.rename(caller_filename + ".tmp", caller_filename)


# run example/modular_class.py for test
