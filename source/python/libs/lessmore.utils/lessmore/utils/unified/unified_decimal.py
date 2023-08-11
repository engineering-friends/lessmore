import re

from decimal import Decimal
from typing import Union

from loguru import logger

from lessmore.utils.numeric.numeric import decimal_round


DecimalLike = Union[str, int, float]


class UnifiedDecimal:
    def __call__(self, value):
        logger.warning("unified_decimal() is deprecated and soon will be removed, use to_decimal() instead")
        return UnifiedDecimal.to_decimal(value)

    @staticmethod
    def is_number_like(value: str):
        return re.search(r"^[+-]*(\d+(?:\.\d+)?)$", value)

    @staticmethod
    def to_decimal(value, is_stripped=True, max_precision=16):
        if isinstance(value, str):
            # - Validate

            assert UnifiedDecimal.is_number_like(value)

            # - Convert to float

            value = float(value)

            # - Return

            return unified_decimal.to_decimal(value, max_precision=max_precision, is_stripped=is_stripped)

        elif isinstance(value, int):
            return Decimal(value)
        elif isinstance(value, float):
            return decimal_round(value, Decimal("1.0"), precision=max_precision, is_stripped=is_stripped)
        else:
            raise Exception(f"Unknown decimal format: {type(value)}")

    @staticmethod
    def to_str(value):
        value = UnifiedDecimal.to_decimal(value)
        return str(value)

    @staticmethod
    def to_string(value):
        logger.warning("UnifiedDecimal.to_string is deprecated, use UnifiedDecimal.to_str instead")
        return UnifiedDecimal.to_str(value)

    @staticmethod
    def to_float(value):
        value = UnifiedDecimal.to_decimal(value)
        return float(value)


unified_decimal = UnifiedDecimal()


def to_decimal(value, is_stripped=True, max_precision=16):
    return unified_decimal.to_decimal(value, is_stripped=is_stripped, max_precision=max_precision)


def to_decimal_str(value):
    return unified_decimal.to_str(value)


def to_decimal_float(value):
    return unified_decimal.to_float(value)


def test():
    assert to_decimal(1) == Decimal(1)
    assert to_decimal("1.0") == Decimal(1)
    assert to_decimal_float("1.4") == 1.4
    assert to_decimal(1 / 3) == Decimal("0.3333333333333333")
    assert str(to_decimal("0.3333333333333333111")) == "0.3333333333333333"
    assert str(to_decimal("1.00000")) == "1"
    assert to_decimal(1 / 3, max_precision=3) == Decimal("0.333")
    assert str(to_decimal(1.00, max_precision=3)) == "1"


if __name__ == "__main__":
    test()
