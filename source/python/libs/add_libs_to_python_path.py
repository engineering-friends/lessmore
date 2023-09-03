import glob
import os
import sys

from pathlib import Path


def add_libs_to_python_path():
    for path in glob.glob(str(Path(__file__).parent / "*")):
        if os.path.isdir(path) and path not in sys.path:
            sys.path.append(path)
