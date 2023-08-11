from datetime import timedelta

from lessmore.utils.numeric.numeric import custom_round
from lessmore.utils.to_anything.unified_datetime import to_datetime, to_timestamp
from lessmore.utils.to_anything.unified_timedelta import to_seconds, to_timedelta


def round_datetime(dt_obj, td_obj, rounding="nearest_half_even"):
    assert to_timedelta(td_obj) < timedelta(days=1), "Only rounding less than a day is supported."
    ts = to_timestamp(dt_obj)
    ts = custom_round(a=ts, b=to_seconds(td_obj), rounding=rounding)
    return to_datetime(ts)


def test():
    # todo next: fixt tests

    assert round_datetime(to_datetime("2021-01-01 00:29:00"), to_timedelta("1h")) == to_datetime("2021-01-01 00:00:00")
    assert round_datetime(to_datetime("2021-01-01 00:30:00"), to_timedelta("1h")) == to_datetime("2021-01-01 00:00:00")
    assert round_datetime(to_datetime("2021-01-01 00:31:00"), to_timedelta("1h")) == to_datetime("2021-01-01 01:00:00")


if __name__ == "__main__":
    test()
