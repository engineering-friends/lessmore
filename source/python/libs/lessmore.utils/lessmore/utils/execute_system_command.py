import os
import shlex
import subprocess

from typing import Optional, Union


def execute_system_command(
    cmd: Union[str, list],
    timeout: int = 60,
    working_directory: Optional[str] = None,
):
    # - Get current working directory

    old_working_directory = os.getcwd()

    # - Set new current directory if needed

    if working_directory:
        os.chdir(working_directory)

    # convert to list of command arguments

    # split cmd by space, but not if it is in quotes

    if isinstance(cmd, str):
        cmd = shlex.split(cmd)  # "a b c" -> ["a", "b", "c"]

    try:
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=timeout).decode()
        except subprocess.TimeoutExpired as e:
            raise Exception(f"Failed to execute system command, timeout expired: {str(e)}")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to execute system command: {str(e)}-{e.output.decode()}")
        except Exception as e:
            raise Exception(f"Failed to execute system command: {str(e)}")
    except:
        # - Restore current directory if needed no matter the outcome

        if working_directory:
            os.chdir(old_working_directory)

        # - Raise original exception

        raise


def test():
    try:
        execute_system_command("sleep 10", timeout=1)

    except Exception as e:
        assert "Command '['sleep', '10']' timed out after 1 seconds" in str(e)

    assert execute_system_command("echo 1") == "1\n"


if __name__ == "__main__":
    test()
