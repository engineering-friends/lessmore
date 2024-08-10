from inline_snapshot import external, outsource, snapshot
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests
from loguru import logger


def test():
    # - Logs

    print("Print message from test")

    logger.debug("Debug message")

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
    run_snapshot_tests()
