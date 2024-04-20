import os
import time

import pytest

from inline_snapshot import external, outsource, snapshot
from loguru import logger

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru


def test1():
    print("Print message from test 1")


def test2():
    # - Logs

    print("Print message from test 2")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # - Inline snapshot

    assert "value" == snapshot("value")
    assert 5 <= snapshot(5)
    assert 5 in snapshot([5])

    a = snapshot({"key": "value"})
    assert a["key"] == "value"

    assert outsource(
        "Long data" * 1000,
        suffix=".png",  # defaults to .bin for bytes and .txt for str
    ) == snapshot(external("dc9b148c966a*.png"))


@pytest.fixture(autouse=True)
def run_around_tests():
    print("\n" + "─" * 88)
    yield
    print("\n")


if __name__ == "__main__":
    configure_loguru()
    pytest.main(
        args=[
            __file__,
            "--inline-snapshot=create",
            "--capture=no",  # disables capturing of print calls
            "--log-cli-level=INFO",  # enables "live logs": logging records are shown immediately as they happen
            "--disable-warnings",
        ]
    )
