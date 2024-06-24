"""Tqdm wrapper with more functionality."""

import time

from datetime import datetime
from typing import Any, Callable, Optional

import pytest

from tqdm import tqdm


class track:
    """Simple tqdm wrapper with more functionality."""

    def __init__(
        self,
        *args,  # passed to tqdm backend
        desc: Optional[Callable] = None,
        postfix: Optional[Callable[[Any], dict]] = lambda value: {"value": str(value)[:128]},
        timing_format="%H:%M:%S",
        hook: Optional[Callable] = None,
        **kwargs,  # passed to tqdm backend
    ):
        # - Save parameters

        self.desc = desc
        self.postfix = postfix
        self.hook = hook
        self.timing_format = timing_format

        self.tqdm_instance = tqdm(*args, **kwargs)

        # - Capture start time

        self.start = datetime.now()

    def __iter__(self):
        for value in self.tqdm_instance.__iter__():
            # - Get desc

            desc = str(self.desc(value)) if self.desc else None

            if desc:
                self.tqdm_instance.set_description(desc)

            if self.postfix:
                self.tqdm_instance.set_postfix(self.postfix(value))

            if self.hook:
                self.hook(value)

            yield value


@pytest.mark.slow
def test():
    def sample_hook(i):
        if i % 100 == 0:
            print("\nThis is a hook message", i)

    for _ in track(
        range(200),
        hook=sample_hook,
    ):
        time.sleep(0.01)


if __name__ == "__main__":
    test()
