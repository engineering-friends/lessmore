import re

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from dateutil.parser import parse as parse_date
from dateutil.tz import tzutc

from lessmore.utils.numeric.numeric import custom_round


# NOTE: slow
def parse_human_timestamp_re(hts, min_date_str="2000"):
    """
    :param hts: Human timestamp: 20180101/2018010112/201801011200/20180101120000/20180101120000123...
    :return:
    """
    ts_PATTERN = re.compile(r"(\d{4})(\d{2})(\d{2})(\d{2})?(\d{2})?(\d{2})?(\d+)?")
    hts = str(hts)

    if hts < min_date_str:
        raise Exception("Min date test failed")

    split = list(ts_PATTERN.match(hts).groups()[: int((len(hts) - 2) / 2)])

    # adjust microseconds
    if len(split) == 7:
        split[-1] = split[-1].ljust(6, "0")[:6]

    return datetime(*map(int, split))


def parse_human_timestamp(hts, min_date_str="2000"):
    """
    :param hts: Human timestamp: 20180101/2018010112/201801011200/20180101120000/20180101120000123...
    :return:
    """
    hts = str(hts)

    if hts < min_date_str:
        raise Exception("Min date test failed")

    slices = [
        slice(0, 4),
        slice(4, 6),
        slice(6, 8),
        slice(8, 10),
        slice(10, 12),
        slice(12, 14),
        slice(14, None),
    ][: int((len(hts) - 2) / 2)]

    split = [hts[sl] for sl in slices]

    # adjust microseconds
    if len(split) == 7:
        split[-1] = split[-1].ljust(6, "0")[:6]

    return datetime(*map(int, split))


def to_hts(dt_obj):
    dt_obj = to_datetime(dt_obj)
    return int(dt_obj.strftime("%Y%m%d%H%M%S%f")[:-3])


def to_datetime(dt_obj, none_invariant=True):
    """
    :param dt_obj: datetime-like object: datetime.datetime or str
    :return: datetime

    is_utc =
    NOTE: This is slow
    """
    if isinstance(dt_obj, datetime):
        return dt_obj
    elif isinstance(dt_obj, str) and not is_freq(dt_obj):
        try:
            return parse_human_timestamp(dt_obj)
        except:
            pass

        # '01.08.2019' type
        search = re.search(r"(\d\d)\.(\d\d)\.(\d\d\d\d)", dt_obj)
        if search:
            d, m, y = search.groups()
            return datetime(int(y), int(m), int(d))

        # '01.08.20' type
        for pat in [
            r"^(\d\d)\.(\d\d)\.(\d\d)$",
            r"^\d(\d\d)\.(\d\d)\.(\d\d)$",
            r"^\d(\d\d)\.(\d\d)\.(\d\d)^\d",
            r"^(\d\d)\.(\d\d)\.(\d\d)\d",
        ]:
            search = re.search(pat, dt_obj)
            if search:
                d, m, y = search.groups()
                return datetime(int(y) + 2000, int(m), int(d))

        dt = parse_date(dt_obj)
        if dt and dt.tzinfo:
            dt = dt.astimezone(tzutc()).replace(tzinfo=None)
        return dt

    elif none_invariant and dt_obj is None:
        return None
    elif isinstance(dt_obj, (int, float, np.integer)):
        try:
            return parse_human_timestamp(dt_obj)
        except:
            pass

        try:
            return parse_date(str(dt_obj))
        except:
            pass

        try:
            return datetime.fromtimestamp(dt_obj, tz=timezone.utc).replace(tzinfo=None)
        except:
            pass

        return datetime.fromtimestamp(dt_obj / 1000, tz=timezone.utc).replace(tzinfo=None)
    else:
        raise Exception("Unknown datetime-like object type")


to_dt = to_datetime


def to_timestamp(dt_obj):
    """
    :param dt_obj: naive datetime
    :return:
    """
    dt_obj = to_datetime(dt_obj)
    # timestamp is always in utc!
    return dt_obj.replace(tzinfo=timezone.utc).timestamp()


to_ts = to_timestamp


def to_mts(dt_obj):
    return to_timestamp(dt_obj) * 1000


def to_str(dt, format=None):
    if isinstance(dt, str):
        return dt
    elif isinstance(dt, datetime):
        if not format:
            return str(dt)
        return dt.strftime(format)
    else:
        raise Exception("Unsupported type")


def get_strptime_pattern(s):
    """
    :param s: str
    :return: get strptime pattern

    NOTE: be careful with microseconds. It is not handled properly
    """
    if len(s) > 20:
        raise Exception("Too big string")

    return "%Y%m%d%H%M%S%f"[: int(len(s) - 2)]


def to_datetime_series(s):
    """
    :param s: a series of datetime-like objects with the same prototype.
    :return: a datetime series
    """

    sample = s.iloc[0]
    # process hts case
    try:
        parse_human_timestamp(sample)
    except:
        pass
    else:
        sample = str(sample)
        pattern = get_strptime_pattern(sample)
        s = s.astype(str)

        # 20 is for full %Y%m%D%H%M%S%f and 17 is for the same format, but when %f is replaced with 3 digits, not 6 as is by default
        if len(sample) > 20:
            # crop to microseconds
            s = s[:20]
        elif len(sample) >= 17:
            # add zeros for microseconds
            s = s + "0" * (20 - len(sample))
        return pd.to_datetime(s, format=pattern)

    if isinstance(sample, (int, np.integer)):
        # considered as timestamp: 1521193807
        int_part = str(sample).split(".")[0]
        # '1521193807'
        if len(int_part) == 10:
            return pd.to_datetime(s, unit="s")
        # '1521193807000'
        elif len(int_part) == 13:
            return pd.to_datetime(s, unit="ms")
        # '1521193807000000'
        elif len(int_part) == 16:
            return pd.to_datetime(s, unit="us")
        # '1521193807000000000'
        elif len(int_part) == 19:
            return pd.to_datetime(s, unit="ns")

    elif isinstance(sample, (float, np.float64)):
        # considered as timestamp: 1521193807
        int_part = str(sample).split(".")[0]
        # '1521193807'
        if len(int_part) == 10:
            return s.apply(datetime.utcfromtimestamp)
        # '1521193807000'
        elif len(int_part) == 13:
            return (s / 1000).apply(datetime.utcfromtimestamp)
    return pd.to_datetime(s, infer_datetime_format=True)


def cast_datetime_many(lst):
    # NOTE: THIS CODE INFERS DATETIME FORMAT! In other words, all passed values should have the same format
    return to_datetime_series(pd.Series(lst)).tolist()


cast_dt_series = to_datetime_series


def to_freq(td_obj, keys=None):
    """
    :param td: `datetime.timedelta`
    :return: string of {}D{}H{}T{}S format for `pandas.Grouper`
    """
    td = cast_timedelta(td_obj)
    keys = keys or ["d", "h", "m", "s"]
    d = td.days
    h = td.seconds // 3600
    m = (td.seconds // 60) % 60
    s = td.seconds - (3600 * h + 60 * m)
    vals = [d, h, m, s]

    res = ""
    for i in range(4):
        if vals[i] != 0:
            res += f"{vals[i]}{keys[i]}"
    return res


def parse_freq(freq_str, keys=None):
    keys = keys or ["d", "h", "m", "s"]
    ts_PATTERN = re.compile(r"^((\d+){})?((\d+){})?((\d+){})?((\d+){})?$".format(*keys))
    groups = ts_PATTERN.match(freq_str).groups()

    if len(groups) % 2 != 0:
        raise Exception("Bad input str")
    groups = groups[::2]

    period_secs = [3600 * 24, 3600, 60, 1]
    secs_dict = dict(zip(keys, period_secs))

    if not any(groups):
        raise Exception("Bad input str")

    secs = 0
    for group in groups:
        if not group:
            continue
        key = group[-1]
        val = int(group[:-1])
        if key not in secs_dict:
            raise Exception("Bad input str")
        secs += val * secs_dict[key]
    return timedelta(seconds=secs)


def is_freq(freq_str, keys=None):
    try:
        parse_freq(freq_str, keys=keys)
    except:
        return False
    return True


def cast_timedelta(td_obj):
    if isinstance(td_obj, timedelta):
        return td_obj
    elif isinstance(td_obj, (int, float, np.integer)):
        return timedelta(seconds=td_obj)
    elif isinstance(td_obj, str):
        try:
            return timedelta(seconds=int(td_obj))
        except:
            pass
        return parse_freq(td_obj)
    else:
        raise Exception("Unknown td_obj format")


cast_td = cast_timedelta


def to_seconds(td_obj):
    if isinstance(td_obj, (int, float)):
        return td_obj
    return cast_timedelta(td_obj).total_seconds()


def to_dateoffset(td_obj):
    # https://pandas.pydata.org/pandas-docs/stable/timeseries.html
    return to_freq(td_obj, keys=["D", "H", "T", "S"])


def round_datetime(dt_obj, td_obj, rounding="nearest_half_even"):
    assert cast_timedelta(td_obj) < timedelta(days=1), "Only rounding less than a day is supported."
    ts = to_timestamp(dt_obj)
    ts = custom_round(ts, to_seconds(td_obj), rounding)
    return to_datetime(ts)


def timestamp_to_utc_str(timestamp: int):
    """
    Convert timestamp to UTC format string

    :param timestamp: 549878451578

    :return: str "2013-10-21T13:28:06.419Z"
    """
    utc_at = datetime.utcfromtimestamp(int(timestamp))
    return utc_at.strftime("%Y-%m-%dT%H:%M:%S") + utc_at.strftime(".%f")[:4] + "Z"


def test():
    print(to_datetime(datetime.now()))
    print(to_datetime("20180101"))
    print(to_datetime(20180101))

    import time

    print(time.time(), to_datetime(time.time()))
    print(to_datetime(str(datetime.now())))

    dt1 = to_datetime("2018-01-01 12:00:00")
    ts = to_timestamp(dt1)
    dt2 = to_datetime(ts)
    dt3 = to_datetime(ts)
    print(dt1, dt2, dt3)
    print(parse_human_timestamp(20180101120000123123123))
    print(parse_human_timestamp(20180101120000123))

    print(datetime.now().strftime("%f"))
    print(to_hts(datetime.now()))
    print(datetime.fromtimestamp(1500021000))
    print(datetime.utcfromtimestamp(1500021000))

    print(to_datetime(20170720000000000))

    print(to_datetime(1))
    print(parse_freq("4d1s"))
    print(cast_timedelta("4d5m"))
    print(cast_timedelta(300))
    print(to_freq(300))
    print(cast_timedelta("5m"))

    print(to_dt(1522783575000))

    print(to_datetime("Thu May 31 19:34:16 2018 +0000"))
    print(to_datetime("Thu May 31 19:34:16 2018 +0300"))

    print(round_datetime(to_datetime("2018-01-01 12:00:05"), 300))
    print(round_datetime(to_datetime("2018-01-01 12:00:05"), 300, "ceil"))
    print(round_datetime(to_datetime("2018-01-01 12:00:05"), 300, "floor"))
    print(round_datetime(to_datetime("2018-01-01 23:30:00"), 300, "floor"))


if __name__ == "__main__":
    test()
