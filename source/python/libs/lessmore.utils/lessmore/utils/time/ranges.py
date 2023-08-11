import calendar

from datetime import datetime, timedelta


def add_months(dt, n):
    month = dt.month - 1 + n
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)


def iter_range_by_months(beg, end):
    if beg >= end:
        return
    while True:
        next_end = add_months(datetime(beg.year, beg.month, 1), 1)  # first day of next month
        next_end = min(next_end, end)
        yield beg, next_end
        beg = next_end

        if next_end == end:
            return


def _get_quarter_by_month(month_name):
    if month_name in range(1, 4):
        return "Q1"
    elif month_name in range(4, 7):
        return "Q2"
    elif month_name in range(7, 10):
        return "Q3"
    elif month_name in range(10, 13):
        return "Q4"


def iter_quarters(beg, end):
    cur_beg = beg
    for _beg, _end in iter_range_by_months(beg, end):
        if _end.month in [4, 7, 10, 1]:
            yield _beg.year, _get_quarter_by_month(_beg.month), cur_beg, _end
            cur_beg = _end

        if _end == end and cur_beg != _end:
            # last value
            yield _beg.year, _get_quarter_by_month(_beg.month), cur_beg, _end


def iter_range(beg, end, period):
    while beg < end:
        next_beg = beg + period
        next_beg = min(next_beg, end)
        yield beg, next_beg
        beg = next_beg


def datetime_range(start_at, period=None, stop_at=None, n=None):
    if stop_at:
        while start_at < stop_at:
            yield start_at
            start_at = min(start_at + period, stop_at)
    elif n:
        for i in range(n):
            yield start_at + i * period
    else:
        raise Exception("Specify stop_at or n")


def test_ranges():
    from utils_ak.time import cast_datetime, cast_timedelta

    # add months
    dt = cast_datetime("2020.01.30")
    for i in range(12):
        print(add_months(dt, i))

    # iter range by months
    print(list(iter_range_by_months(cast_datetime("2020.01.15"), cast_datetime("2020.02.16"))))
    print(list(iter_range_by_months(cast_datetime("2020.01.01"), cast_datetime("2020.06.01"))))

    # iter range
    print(
        list(
            iter_range(
                cast_datetime("2020.01.01 12:00:00"),
                cast_datetime("2020.01.01 12:16:00"),
                cast_timedelta("5m"),
            )
        )
    )

    print(list(iter_quarters(cast_datetime("2020.02.15"), cast_datetime("2020.07.15"))))

    print(
        list(
            datetime_range(
                cast_datetime("2020.01.01"),
                period=timedelta(days=1),
                stop_at=cast_datetime("2020.01.04"),
            )
        )
    )
    print(list(datetime_range(cast_datetime("2020.01.01"), period=timedelta(days=1), n=3)))


if __name__ == "__main__":
    test_ranges()
