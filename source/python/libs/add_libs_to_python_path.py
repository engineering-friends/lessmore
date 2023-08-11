import glob
import os
import sys


def add_libs_to_python_path():
    directory_names = [
        directory_name
        for directory_name in glob.glob(os.path.join(os.path.dirname(__file__), "*"))
        if os.path.isdir(directory_name)
    ]

    for path in directory_names:
        if path not in sys.path:
            sys.path.append(path)
