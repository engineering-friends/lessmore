import os
import platform
import subprocess


def open_file_in_os(fn):
    fn = os.path.abspath(fn)
    if platform.system() == "Darwin":  # macOS
        subprocess.call(("open", fn))
    elif platform.system() == "Windows":  # Windows
        os.startfile(fn)
    else:  # linux variants
        subprocess.call(("xdg-open", fn))
