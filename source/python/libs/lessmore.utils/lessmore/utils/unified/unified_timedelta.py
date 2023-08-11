import re

from datetime import timedelta
from typing import Union

from loguru import logger


TimedeltaLike = Union[list, int, float, str, timedelta]

# todo later: add pendulum timedelta [@marklidenberg]
# todo later: add kwargs when parsing timedelta (and in other unifiers too) [@marklidenberg]


class UnifiedTimedelta:
    def __call__(self, value):
        logger.warning("unified_timedelta() is deprecated and soon will be removed, use to_timedelta() instead")
        return UnifiedTimedelta.to_timedelta(value)

    @staticmethod
    def to_timedelta(value):
        if isinstance(value, timedelta):
            return value
        elif isinstance(value, str):

            # frequency like "5m"
            value = value.replace(" ", "")
            for keys in [
                ["d", "h", "m", "s"],  # frequency
                ["d", "h", "t", "s"],  # dateoffset
            ]:
                try:
                    groups = re.search(
                        r"^((\d+){})?((\d+){})?((\d+){})?((\d+){})?$".format(*keys), value.lower()
                    ).groups()

                    if len(groups) % 2 != 0:
                        raise Exception("Bad input str")

                    groups = groups[::2]

                    period_seconds = [3600 * 24, 3600, 60, 1]
                    seconds_dict = dict(zip(keys, period_seconds))

                    if not any(groups):
                        raise Exception("Bad input str")

                    seconds = 0
                    for group in groups:
                        if not group:
                            continue
                        key = group[-1]
                        frequency_value = int(group[:-1])
                        if key not in seconds_dict:
                            raise Exception("Bad input str")
                        seconds += frequency_value * seconds_dict[key]
                    return timedelta(seconds=seconds)
                except:
                    pass

            raise Exception(f"Unknown timedelta string: {value}")

        elif isinstance(value, (int, float)):
            return timedelta(seconds=value)
        else:
            raise Exception("Unknown list type")

    @staticmethod
    def to_seconds(value):
        if isinstance(value, (int, float)):
            return value
        else:
            value = UnifiedTimedelta.to_timedelta(value)
            return value.total_seconds()

    @staticmethod
    def to_frequency(value, keys=None):
        value = UnifiedTimedelta.to_timedelta(value)

        keys = keys or ["d", "h", "m", "s"]
        d = value.days
        h = value.seconds // 3600
        m = (value.seconds // 60) % 60
        s = value.seconds - (3600 * h + 60 * m)
        frequency_values = [d, h, m, s]

        result = ""
        for i in range(4):
            if frequency_values[i] != 0:
                result += f"{frequency_values[i]}{keys[i]}"
        return result

    @staticmethod
    def to_dateoffset(value):

        # https://pandas.pydata.org/pandas-docs/stable/timeseries.html
        return UnifiedTimedelta.to_frequency(value, keys=["D", "H", "T", "S"])


unified_timedelta = UnifiedTimedelta()


def to_timedelta(value):
    return unified_timedelta.to_timedelta(value)


# todo later: mabye: return int if possible? [@marklidenberg]


def to_nanoseconds(value):
    return unified_timedelta.to_seconds(value) * 1_000_000_000


def to_microseconds(value):
    return unified_timedelta.to_seconds(value) * 1_000_000


def to_milliseconds(value):
    return unified_timedelta.to_seconds(value) * 1000


def to_seconds(value):
    return unified_timedelta.to_seconds(value)


def to_minutes(value):
    return unified_timedelta.to_seconds(value) / 60


def to_hours(value):
    return unified_timedelta.to_seconds(value) / 3600


def to_days(value):
    return unified_timedelta.to_seconds(value) / 3600 / 24


def to_frequency(value):
    return unified_timedelta.to_frequency(value)


def to_dateoffset(value):
    return unified_timedelta.to_dateoffset(value)


def test():
    for value in ["2m", "2T", 120, 120.0]:
        assert to_timedelta(value) == timedelta(seconds=120)
    assert to_frequency(timedelta(seconds=120)) == "2m"
    assert to_dateoffset("2m") == "2T"
    assert to_seconds("2m") == 120
