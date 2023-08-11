from typing import Union

from loguru import logger


BytesLike = Union[bytes, str]


class UnifiedBytes:
    def __call__(self, value):
        logger.warning("unified_bytes() is deprecated and soon will be removed, use to_bytes() instead")
        return UnifiedBytes.to_bytes(value)

    @staticmethod
    def to_bytes(value, encoding="utf-8"):
        if isinstance(value, bytes):
            return value
        elif isinstance(value, str):
            return value.encode(encoding)
        else:
            raise Exception(f"Unknown bytes format: {type(value)}")

    @staticmethod
    def to_str(value, encoding="utf-8"):
        if isinstance(value, str):
            return value
        elif isinstance(value, bytes):
            return value.decode(encoding)

    @staticmethod
    def to_string(value, encoding="utf-8"):
        logger.warning("UnifiedBytes.to_string is deprecated, use UnifiedBytes.to_str instead")
        return UnifiedBytes.to_str(value, encoding)


unified_bytes = UnifiedBytes()


def to_bytes(value, encoding="utf-8"):
    return unified_bytes.to_bytes(value, encoding)


def to_bytes_str(value, encoding="utf-8"):
    return unified_bytes.to_str(value, encoding)


def test():
    assert to_bytes("foo") == b"foo"
    assert to_bytes_str(b"foo") == "foo"
    assert to_bytes_str("foo") == "foo"


if __name__ == "__main__":
    test()
