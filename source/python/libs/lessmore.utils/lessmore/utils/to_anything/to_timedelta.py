import re

from datetime import timedelta
from typing import Union


TimedeltaLike = Union[list, int, float, str, timedelta]


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
                groups = re.search(r"^((\d+){})?((\d+){})?((\d+){})?((\d+){})?$".format(*keys), value.lower()).groups()

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


def get_frequency(td: timedelta, keys: list = ["d", "h", "m", "s"]):
    d = td.days
    h = td.seconds // 3600
    m = (td.seconds // 60) % 60
    s = td.seconds - (3600 * h + 60 * m)
    frequency_values = [d, h, m, s]

    result = ""
    for i in range(4):
        if frequency_values[i] != 0:
            result += f"{frequency_values[i]}{keys[i]}"
    return result


def test():
    for value in ["2m", "2T", 120, 120.0]:
        assert to_timedelta(value) == timedelta(seconds=120)
    assert get_frequency(timedelta(seconds=120)) == "2m"
