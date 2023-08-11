import fnmatch
import os
import re
import shutil
import subprocess
import sys

from distutils.util import strtobool
from typing import Optional

import fire


# - Utils


def list_files(path: str, pattern: Optional[str] = None, is_recursive: bool = True, is_absolute: bool = True):
    """List files in a path."""
    if not is_recursive:
        fns = os.listdir(path)
    else:
        fns = []
        for root, dirs, files in os.walk(path):
            fns += [os.path.join(root, fn) for fn in files]
    if pattern:
        fns = [fn for fn in fns if fnmatch.fnmatch(fn, pattern)]

    if is_absolute:
        fns = [os.path.abspath(fn) for fn in fns]
    return fns


def execute_system_command(command: str):
    print("Executing command:", command)
    response = subprocess.run(command, capture_output=True, shell=True, text=True)
    return response.stdout, response.stderr


# - Helpers


def _locate_project_python_version():
    # find poetry environment that will work
    for minor in range(15, 0, -1):  # try to use as latest version as possible
        python_version = f"python3.{minor}"  # up to 15 version
        stdout, stderr = execute_system_command(f"poetry env use {python_version}")
        if "EnvCommandError" in stdout + stderr:
            # try next python version
            continue
        elif "NoCompatiblePythonVersionFound" in stdout + stderr:
            # try next python version
            continue
        else:
            # found python
            print(f"Selected python distribution for {os.getcwd()}: {python_version}")
            return python_version

    raise Exception("Failed to find python distribution for current poetry project")


# - Functions


def is_running_in_docker():
    path = "/proc/self/cgroup"
    return os.path.exists("/.dockerenv") or os.path.isfile(path) and any("docker" in line for line in open(path))


def setup_poetry_environments(path: str = "../", force_reinstall: bool = False):
    # - Check if running in docker

    if is_running_in_docker():
        raise Exception("Running in docker container. Local python interpreter instead")

    # - Init arguments

    path = os.path.abspath(path)
    if not path:
        raise Exception("Root not specified")

    # - Setup helper variables

    interpreter_paths = []  # will be filled later
    old_cwd = os.getcwd()

    # - Iterate over python projects

    for pyproject_filename in list_files(path, pattern="*pyproject.toml"):
        # - Get into project directory

        pyproject_dirname = os.path.dirname(pyproject_filename)

        print(f"Running poetry install in {pyproject_filename}...")

        os.chdir(pyproject_dirname)

        # - Set environment_path

        environment_path = os.path.join(pyproject_dirname, ".venv/")

        # - Save interpreter path

        interpreter_paths.append(os.path.join(environment_path, "bin/python"))

        # - Remove old environment if necessary

        if force_reinstall and os.path.exists(environment_path):
            shutil.rmtree(environment_path)

        # - Raise if conflicting old environment exists

        if os.path.exists(environment_path):
            print("Poetry environment already installed")
            continue

        # - Setup poetry distribution

        stdout, stderr = execute_system_command(f"poetry env use {_locate_project_python_version()}; poetry install")

        print(stdout + stderr)

        # - Raise if failed

        if stderr:
            os.chdir(old_cwd)
            raise Exception(f"Failed to install poetry in {pyproject_filename}")

    # - Change directory to initial one

    os.chdir(old_cwd)

    # - Print interpreter paths

    print()
    print(">>> Interpreter paths. Use them to configure pycharm interpreters")
    for interpreter_path in interpreter_paths:
        print(interpreter_path)
    print("<<<")


if __name__ == "__main__":
    fire.Fire(setup_poetry_environments)
