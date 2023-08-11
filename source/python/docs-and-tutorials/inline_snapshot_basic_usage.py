import datetime

from inline_snapshot import snapshot


def something():
    return {
        "name": "hello",
        "one number": 5,
        "numbers": list(range(10)),
        "sets": {1, 2, 15},
        "datetime": datetime.date(1, 2, 22),
        "complex stuff": 5j + 3,
        "bytes": b"fglecg\n\x22",
    }


def test_something():
    """

    # Before running tests
    assert something() == snapshot()

    # After running tests
    assert something() == snapshot(
        {
            "name": "hello",
            "one number": 5,
            "numbers": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "sets": {1, 2, 15},
            "datetime": datetime.date(1, 2, 22),
            "complex stuff": (3 + 5j),
            "bytes": b'fglecg\n"',
        }
    )
    """

    # try it yourself
    assert something() == snapshot()


if __name__ == "__main__":
    import pytest

    # pytest.main(args=[__file__, "--update-snapshots=all"]) # update all snapshots
    pytest.main(args=[__file__, "--update-snapshots=new"])  # update new snapshots
    # pytest.main(args=[__file__, "--update-snapshots=failing"]) # update failing snapshots
    # pytest.main(args=[__file__, "--update-snapshots=none"]) # do not update snapshots
