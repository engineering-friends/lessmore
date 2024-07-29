import os
import subprocess

from typing import Optional, Union


def run_system_command(
    command: Union[str, list],
    timeout: int = 60,
    working_dir: Optional[str] = None,
) -> str:
    # - Append cd command to the command if working_dir is provided

    if working_dir:
        command = f"cd {working_dir} && {command}"

    # - Run the command

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            shell=True,
            timeout=timeout,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error occurred while running the command: {e.stderr}")


def test():
    # - Test run_system_command

    assert run_system_command("echo 1") == "1\n"

    # - With timeout

    try:
        run_system_command("sleep 10", timeout=1)
    except Exception as e:
        assert "Command 'sleep 10' timed out after 1 seconds" in str(e)

    # - With working directory

    os.makedirs("/tmp/run_system_command_test/", exist_ok=True)

    assert run_system_command("pwd", working_dir="/tmp/run_system_command_test/") == "/tmp/run_system_command_test\n"


if __name__ == "__main__":
    test()
