from datetime import UTC, date, datetime
from typing import Union

import pendulum

from dateutil.parser import parse as parse_date


COMMON_DATETIME_PATTERNS = [
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%Y.%m.%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y%m%d%H%M%S",
    "%Y%m%d",
    "%Y-%m-%d--%H-%M-%S",  # filename safe pattern
    "%Y-%m-%d--%H-%M-%S--%f",  # filename safe pattern
    "%Y-%m-%dT%H:%M:%SZ",  # ISO8061
    "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO8061
]

DatetimeLike = Union[datetime, pendulum.DateTime, str, int, float]


def to_datetime(
    value: DatetimeLike,
    parse_date_kwargs: dict = {},
) -> datetime:
    if isinstance(value, datetime) and not isinstance(value, pendulum.DateTime):
        if value.tzinfo:
            value = value.astimezone(pendulum.UTC).replace(tzinfo=None)
        return value
    elif isinstance(value, date) and not isinstance(value, datetime):
        return datetime(value.year, value.month, value.day)
    elif isinstance(value, pendulum.DateTime):
        return to_datetime(value.in_timezone(pendulum.UTC).timestamp())
    elif isinstance(value, (int, float)):
        # - Try in seconds

        try:
            return datetime.fromtimestamp(value, pendulum.tz.UTC).replace(tzinfo=None)
        except:
            # too small or too big
            pass

        # - Try in milliseconds

        try:
            return datetime.fromtimestamp(value / 1_000, pendulum.tz.UTC).replace(tzinfo=None)
        except:
            pass

        # - Try in microseconds

        try:
            return datetime.fromtimestamp(value / 1_000_000, pendulum.tz.UTC).replace(tzinfo=None)
        except:
            pass

        raise Exception(f"Integer out of bounds for datetime: {value}")
    elif isinstance(value, str):
        # - Check if now

        if value.lower() == "now":
            return datetime.now(UTC).replace(tzinfo=None)

        # - Try most common patterns

        for pattern in COMMON_DATETIME_PATTERNS:
            try:
                return datetime.strptime(value, pattern)
            except:
                continue

        # - Try dateutils.parser.parse

        try:
            result = parse_date(value, **parse_date_kwargs)
            if result and result.tzinfo:
                result = result.astimezone(pendulum.UTC).replace(tzinfo=None)
            return result
        except:
            pass

        raise Exception(f"Unknown string datetime format: {value}")
    raise Exception("Unknown datetime type")


def to_timestamp(value: DatetimeLike):
    return to_datetime(value).replace(tzinfo=pendulum.tz.UTC).timestamp()


def test():
    assert to_datetime("2022.01.01") == datetime(year=2022, month=1, day=1)
    assert to_datetime(parse_date("2022-09-05T18:00:00+03:00")) == to_datetime("2022-09-05T15:00:00")
    assert to_datetime(parse_date("2022-09-05T18:00:00+03:00")) == to_datetime("2022-09-05T15:00:00")
    assert to_datetime(to_timestamp("2022.01.01")) == to_datetime("2022.01.01")
    assert to_timestamp("1970.01.01") == 0


if __name__ == "__main__":
    test()
