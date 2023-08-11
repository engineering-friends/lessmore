import inspect

from pathlib import Path


def get_caller_path() -> Path:
    # - Get the current frame

    current_frame = inspect.currentframe()

    # - Go up two frames: One frame up is this function itself. Two frames up is the caller

    caller_frame = inspect.getouterframes(current_frame)[2]

    # - Extract the file name from the frame

    return Path(caller_frame[1])


def test():
    def calling_function():
        print("This function is the caller!")
        print("Caller's file:", get_caller_path())

    calling_function()


if __name__ == "__main__":
    test()
