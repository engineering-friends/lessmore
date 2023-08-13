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
from typing import Union

import numpy as np

from lessmore.utils.round.round_decimal.round_decimal import round_decimal


def relative_round(
    a: Union[float, int, str],
    b: Union[float, int, str],
    rounding: str = ROUND_HALF_EVEN,
    precision: int = 0,
    pre_round_precision: int = 1,
):
    # - Pre round

    if pre_round_precision:
        a = relative_round(
            a=a,
            b=b,
            rounding=ROUND_HALF_DOWN,
            precision=precision + pre_round_precision,
            pre_round_precision=0,
        )

    # - Calculate round(a / b)

    n = a / b * (10**precision)
    n = int(round_decimal(a=n, b=1, rounding=rounding))

    # - Return

    return n * b / (10**precision)


def test():
    assert relative_round(a=3.1, b=0.5) == 3
    assert relative_round(a=3.5, b=0.5) == 3.5


if __name__ == "__main__":
    test()
