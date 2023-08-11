import os

from typing import Callable

from lessmore.utils.unified import to_snake_case


def _build_class_file_content(
    class_name: str,
    class_module_path: str,
    function_to_its_filename: dict[Callable, str],
    extra_import_lines: list[str] = None,
) -> str:
    """Build the content of the modular_class file."""

    # - Init code

    code = "# Auto-generated file. To update the file, simply run it\n\n"

    # - Add function imports

    for function, filename in function_to_its_filename.items():
        # get full module path
        function_filename = os.path.abspath(
            filename
        )  # .../deeplay.utils/deeplay/utils/modular_code/modular_class/example/some_method.py
        function_module_path = (
            function_filename[1:].replace(".py", "").replace("/", ".")
        )  # ....deeplay.utils.deeplay.utils.modular_code.modular_class.example.some_method
        function_module_path = (
            class_module_path + function_module_path.split(class_module_path)[1]
        )  # deeplay.utils.modular_code.modular_class.example.some_method
        code += f"from {function_module_path} import {function.__name__}\n"  # from lessmore.utils.modular_code.modular_class.example.some_method import some_method

    # - Add import for ModularClassData

    code += f"from {class_module_path}.{to_snake_case(class_name + 'Data')} import {class_name}Data\n"  # from lessmore.utils.modular_code.modular_class.modular_class_data import ModularClassData

    # - Add extra import lines

    if extra_import_lines is not None:
        for line in extra_import_lines:
            code += f"{line}\n"

    # - Create class

    code += f"class {class_name}({class_name}Data):\n"
    for self_function in function_to_its_filename.keys():
        code += f"    def {self_function.__name__}(self, *args, **kwargs):\n"
        code += f"        return {self_function.__name__}(self=self, *args, **kwargs)\n"

    # - Add main with update_modular_class_inline call

    code += f"""
if __name__ == '__main__':
    update_modular_class_inline()
"""
    return code


def func(self):
    return "foo"


def test():
    print(
        _build_class_file_content(
            class_name="ModularClass",
            class_module_path="deeplay.utils.modular_code.modular_class",
            function_to_its_filename={func: __file__},
        )
    )


if __name__ == "__main__":
    test()
