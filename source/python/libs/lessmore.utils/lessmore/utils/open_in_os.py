import os
import platform
import subprocess


def open_in_os(filename: str) -> None:
    # - Get absolute path

    filename = os.path.abspath(filename)

    # - Open file

    if platform.system() == "Darwin":
        # macOS
        subprocess.call(("open", filename))
    elif platform.system() == "Windows":
        # Windows
        os.startfile(filename)
    else:
        # linux variants
        subprocess.call(("xdg-open", filename))
