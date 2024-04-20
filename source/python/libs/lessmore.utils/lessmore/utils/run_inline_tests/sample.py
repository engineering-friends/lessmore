from inline_snapshot import external, outsource, snapshot
from loguru import logger

from lessmore.utils.run_inline_tests.run_inline_tests import run_inline_tests, separate_tests


def test():
    # - Logs

    print("Print message from test")

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # - Inline snapshot

    assert "value" == snapshot()
    assert 5 <= snapshot()
    assert 5 in snapshot()

    a = snapshot()
    assert a["key"] == "value"

    assert (
        outsource(
            "Long data" * 1000,
            suffix=".png",  # defaults to .bin for bytes and .txt for str
        )
        == snapshot()
    )


def test_fail():
    raise Exception("An exception occured!")


if __name__ == "__main__":
    run_inline_tests()
