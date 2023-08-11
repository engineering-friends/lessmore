from lessmore.utils.optimize_imports.functions.get_python_filenames import get_python_filenames
from lessmore.utils.optimize_imports.update_init_py_imports import update_init_py_imports


def optimize_imports(dir, update_init_py=True, shorten_imports=True):

    # - Update init py imports

    if update_init_py:
        update_init_py_imports(dir)

    # - Shorten imports in modules

    if shorten_imports:
        for filename in get_python_filenames(dir):
            with open(filename, "r") as f:
                content = f.read()

            with open(filename, "w") as f:
                f.write(shorten_imports(content))
