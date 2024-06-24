""" Math functionality. """
from decimal import (
    ROUND_05UP,
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_FLOOR,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
    Decimal as D,
)


CEIL_UP = "ceil_up"
FLOOW_DOWN = "floor_down"

ROUND_DIC = {
    "nearest_half_even": ROUND_HALF_EVEN,
    "floor": ROUND_FLOOR,
    "ceil": ROUND_CEILING,
    "ceil_up": ROUND_CEILING,
    "floor_down": ROUND_FLOOR,
    "down": ROUND_DOWN,
    "up": ROUND_UP,
    "nearest_half_up": ROUND_HALF_UP,
    "nearest_half_down": ROUND_HALF_DOWN,
    "down_except_0_and_5": ROUND_05UP,
}


def decimal_round(a, b, rounding="nearest_half_even", precision=0, strip=False):
    a, b = D(a), D(b)
    n = a / b / D(".1") ** precision
    _rounding = ROUND_DIC.get(rounding, rounding)
    n_rounded = n.quantize(D("1."), rounding=_rounding)

    if rounding == "ceil_up" and float(n) == float(n_rounded):
        n_rounded = D(int(n_rounded) + 1)
    elif rounding == "floor_down" and float(n) == float(n_rounded):
        n_rounded = D(int(n_rounded) - 1)

    res = n_rounded * b * D(".1") ** precision
    if strip:
        res = strip_decimal(res)
    return res


def custom_round(a, b, rounding="nearest_half_even", precision=0, pre_round_precision=1):
    if pre_round_precision:
        a = custom_round(
            a,
            b,
            "nearest_half_down",
            precision + pre_round_precision,
            pre_round_precision=0,
        )
    n = a / b * (10**precision)
    n = int(decimal_round(n, 1, rounding))
    return n * b / (10**precision)


def cast_decimal(f, precision=15, strip=True):
    d = decimal_round(f, D("1.0"), precision=precision)
    if strip:
        s = str(d)
        s = strip_zeros(s)
        d = D(s)
    return d


def strip_decimal(d):
    return D(strip_zeros(str(d)))


def strip_zeros(s):
    return s.rstrip("0").rstrip(".") if "." in s else s


def test():
    roundings = [
        ROUND_HALF_DOWN,
        ROUND_DOWN,
        ROUND_CEILING,
        ROUND_05UP,
        ROUND_FLOOR,
        ROUND_HALF_EVEN,
        ROUND_HALF_UP,
        ROUND_UP,
    ]
    roundings += list(ROUND_DIC.keys())

    for rounding in roundings:
        for v in [1.99, 1.05, -1.99, -1.05]:
            print(rounding, v, 0.1, custom_round(v, 0.1, rounding))

    # 1.99
    print(decimal_round("1.99", "0.01", rounding="ROUND_FLOOR"))
    # may be 1.98 since 1.99 may be 1.9899999999
    print(decimal_round(1.99, "0.01", rounding="ROUND_FLOOR", precision=0))
    print(decimal_round(1.99, "0.01", rounding="ROUND_FLOOR", precision=2))
    # certainly 1.99, since we round 1.9899999 to 1.99 first
    print(decimal_round(1.99, "0.0100", rounding="ROUND_FLOOR", precision=10))
    print(decimal_round(1.99, "0.0100", rounding="ROUND_FLOOR", precision=10))
    print(decimal_round(1.99, "0.0100", rounding="ROUND_FLOOR", precision=10, strip=True))

    print(custom_round(1.9999999, 1.0, rounding="floor"))
    print(custom_round(1.99999999, 1.0, rounding="floor", pre_round_precision=1))

    print(custom_round(1.01, 1.0, rounding="floor_down", pre_round_precision=0))
    print(custom_round(1.0, 1.0, rounding="floor_down", pre_round_precision=0))


if __name__ == "__main__":
    test()
