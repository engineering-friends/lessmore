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
from typing import Literal, Union


def strip_zeros(s):
    return s.rstrip("0").rstrip(".") if "." in s else s  # 0.000 -> 0, 0.001 -> 0.001


def round_decimal(
    a: Union[float, int, str, D],
    b: Union[float, int, str, D],
    rounding: str = ROUND_HALF_EVEN,
    precision: int = 0,
    strip: bool = False,
):
    """
    Parameters
    ----------
    a : Union[float, int, str]
        Numerator.
    b : Union[float, int, str]
        Denominator.
    rounding : str, optional
        Rounding mode. The default is ROUND_HALF_EVEN.

            decimal.ROUND_CEILING
            Round towards Infinity.

            decimal.ROUND_FLOOR
            Round towards -Infinity.

            decimal.ROUND_DOWN
            Round towards zero.

            decimal.ROUND_UP
            Round away from zero.

            decimal.ROUND_HALF_DOWN
            Round to nearest with ties going towards zero.

            decimal.ROUND_HALF_EVEN
            Round to nearest with ties going to nearest even integer.

            decimal.ROUND_HALF_UP
            Round to nearest with ties going away from zero.

            decimal.ROUND_05UP
            Round away from zero if last digit after rounding towards zero would have been 0 or 5; otherwise round towards zero.

    precision : int, optional
    strip : bool, optional

    """

    # - Preprocess arguments

    a, b = D(a), D(b)

    # - Calculate rounded(a / b)

    ratio = a / b / (D(".1") ** precision)
    n = ratio.quantize(D("1."), rounding=rounding)

    # - Calculate result

    res = n * b * D(".1") ** precision

    # - Strip if needed

    if strip:
        res = D(strip_zeros(str(res)))

    # - Return

    return res


def test():
    assert round_decimal(a=1.1, b=1, rounding=ROUND_CEILING) == 2
    assert round_decimal(a=1.5, b=1, rounding=ROUND_CEILING) == 2
    assert round_decimal(a=1.9, b=1, rounding=ROUND_CEILING) == 2
    assert round_decimal(a=-1.1, b=1, rounding=ROUND_CEILING) == -1
    assert round_decimal(a=-1.5, b=1, rounding=ROUND_CEILING) == -1
    assert round_decimal(a=-1.9, b=1, rounding=ROUND_CEILING) == -1

    assert round_decimal(a=1.1, b=1, rounding=ROUND_FLOOR) == 1
    assert round_decimal(a=1.5, b=1, rounding=ROUND_FLOOR) == 1
    assert round_decimal(a=1.9, b=1, rounding=ROUND_FLOOR) == 1
    assert round_decimal(a=-1.1, b=1, rounding=ROUND_FLOOR) == -2
    assert round_decimal(a=-1.5, b=1, rounding=ROUND_FLOOR) == -2
    assert round_decimal(a=-1.9, b=1, rounding=ROUND_FLOOR) == -2

    assert round_decimal(a=1.1, b=1, rounding=ROUND_UP) == 2
    assert round_decimal(a=1.5, b=1, rounding=ROUND_UP) == 2
    assert round_decimal(a=1.9, b=1, rounding=ROUND_UP) == 2
    assert round_decimal(a=-1.1, b=1, rounding=ROUND_UP) == -2
    assert round_decimal(a=-1.5, b=1, rounding=ROUND_UP) == -2
    assert round_decimal(a=-1.9, b=1, rounding=ROUND_UP) == -2

    assert round_decimal(a=1.1, b=1, rounding=ROUND_DOWN) == 1
    assert round_decimal(a=1.5, b=1, rounding=ROUND_DOWN) == 1
    assert round_decimal(a=1.9, b=1, rounding=ROUND_DOWN) == 1
    assert round_decimal(a=-1.1, b=1, rounding=ROUND_DOWN) == -1
    assert round_decimal(a=-1.5, b=1, rounding=ROUND_DOWN) == -1
    assert round_decimal(a=-1.9, b=1, rounding=ROUND_DOWN) == -1

    assert round_decimal(a=1.1, b=1, rounding=ROUND_HALF_DOWN) == 1
    assert round_decimal(a=1.5, b=1, rounding=ROUND_HALF_DOWN) == 1
    assert round_decimal(a=1.9, b=1, rounding=ROUND_HALF_DOWN) == 2
    assert round_decimal(a=-1.1, b=1, rounding=ROUND_HALF_DOWN) == -1
    assert round_decimal(a=-1.5, b=1, rounding=ROUND_HALF_DOWN) == -1
    assert round_decimal(a=-1.9, b=1, rounding=ROUND_HALF_DOWN) == -2

    assert round_decimal(a=1.1, b=1, rounding=ROUND_HALF_EVEN) == 1
    assert round_decimal(a=1.5, b=1, rounding=ROUND_HALF_EVEN) == 2
    assert round_decimal(a=1.9, b=1, rounding=ROUND_HALF_EVEN) == 2
    assert round_decimal(a=-1.1, b=1, rounding=ROUND_HALF_EVEN) == -1
    assert round_decimal(a=-1.5, b=1, rounding=ROUND_HALF_EVEN) == -2
    assert round_decimal(a=-1.9, b=1, rounding=ROUND_HALF_EVEN) == -2

    assert round_decimal(a=1.1, b=1, rounding=ROUND_HALF_UP) == 1
    assert round_decimal(a=1.5, b=1, rounding=ROUND_HALF_UP) == 2
    assert round_decimal(a=1.9, b=1, rounding=ROUND_HALF_UP) == 2
    assert round_decimal(a=-1.1, b=1, rounding=ROUND_HALF_UP) == -1
    assert round_decimal(a=-1.5, b=1, rounding=ROUND_HALF_UP) == -2
    assert round_decimal(a=-1.9, b=1, rounding=ROUND_HALF_UP) == -2

    assert round_decimal(a=1.1, b=1, rounding=ROUND_05UP) == 1  # DOWN
    assert round_decimal(a=1.5, b=1, rounding=ROUND_05UP) == 1
    assert round_decimal(a=1.9, b=1, rounding=ROUND_05UP) == 1
    assert round_decimal(a=-1.1, b=1, rounding=ROUND_05UP) == -1
    assert round_decimal(a=-1.5, b=1, rounding=ROUND_05UP) == -1
    assert round_decimal(a=-1.9, b=1, rounding=ROUND_05UP) == -1

    assert round_decimal(a=5.1, b=1, rounding=ROUND_05UP) == 6  # UP for 0 and 5
    assert round_decimal(a=5.5, b=1, rounding=ROUND_05UP) == 6
    assert round_decimal(a=5.9, b=1, rounding=ROUND_05UP) == 6
    assert round_decimal(a=-5.1, b=1, rounding=ROUND_05UP) == -6
    assert round_decimal(a=-5.5, b=1, rounding=ROUND_05UP) == -6
    assert round_decimal(a=-5.9, b=1, rounding=ROUND_05UP) == -6


if __name__ == "__main__":
    test()
