from decimal import ROUND_DOWN

from lessmore.utils.round.round_fractional import round_fractional
from lessmore.utils.to_anything.unified_datetime import to_datetime, to_timestamp
from lessmore.utils.to_anything.unified_timedelta import to_seconds, to_timedelta


def round_datetime(dt_obj, td_obj, rounding=ROUND_DOWN):
    ts = to_timestamp(dt_obj)
    ts = round_fractional(
        a=ts,
        b=to_seconds(td_obj),
        rounding=rounding,
        pre_round_precision=0,
    )
    return to_datetime(ts)


def test():
    assert round_datetime(to_datetime("2021-01-01 00:29:00"), to_timedelta("1h")) == to_datetime("2021-01-01 00:00:00")
    assert round_datetime(to_datetime("2021-01-01 00:30:00"), to_timedelta("1h")) == to_datetime("2021-01-01 00:00:00")
    assert round_datetime(to_datetime("2021-01-01 00:59:00"), to_timedelta("1h")) == to_datetime("2021-01-01 00:00:00")


if __name__ == "__main__":
    test()
