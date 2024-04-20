import pytest

from _pytest.runner import CallInfo
from inline_snapshot import external, outsource, snapshot
from loguru import logger

from lessmore.utils.run_inline_tests.run_inline_tests import run_inline_tests, separate_tests


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

    raise Exception("An exception occured!")


if __name__ == "__main__":
    run_inline_tests()
