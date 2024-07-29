import re

from decimal import Decimal
from typing import Union

from lessmore.utils.round.round_decimal import round_decimal


DecimalLike = Union[str, int, float]


def to_decimal(value: DecimalLike, max_precision: int = 16):
    """Convert any number-like value to Decimal."""
    if isinstance(value, str):
        # - Validate

        assert re.search(r"^[+-]*(\d+(?:\.\d+)?)$", value), "Value is not number-like."

        # - Convert to float

        value = float(value)

        # - Return

        return to_decimal(value, max_precision=max_precision)

    elif isinstance(value, int):
        return Decimal(value)
    elif isinstance(value, float):
        return round_decimal(a=value, b=Decimal("1.0"), precision=max_precision, strip=True)
    else:
        raise Exception(f"Unknown decimal format: {type(value)}")


def test():
    assert to_decimal(1) == Decimal(1)
    assert to_decimal("1.0") == Decimal(1)
    assert to_decimal(1 / 3) == Decimal("0.3333333333333333")
    assert str(to_decimal("0.3333333333333333111")) == "0.3333333333333333"
    assert str(to_decimal("1.00000")) == "1"
    assert to_decimal(1 / 3, max_precision=3) == Decimal("0.333")
    assert str(to_decimal(1.00, max_precision=3)) == "1"


if __name__ == "__main__":
    test()
