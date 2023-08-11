import os.path

from datetime import timedelta

from lessmore.utils.apply_recursively import apply_recursively
from lessmore.utils.unified import to_frequency


SUPPORTED_EXTENSIONS = [".env", ".json", ".yaml"]

from lessmore.utils.coder import (  # NOTE: do not delete, used in globals() method
    encode_env,
    encode_json,
    encode_msgpack,
    encode_yaml,
)


def write_config_file(config: dict, filename: str, is_stringified: bool = True) -> None:

    # - Stringify if needed

    if is_stringified:
        config = apply_recursively(
            config,
            lambda inner_value: to_frequency(inner_value) if isinstance(inner_value, timedelta) else str(inner_value),
        )

    # - Get extension

    extension = os.path.splitext(filename)[-1]
    assert extension in SUPPORTED_EXTENSIONS, f"Non supported config extension: {extension}"

    # - Get encoder

    encoder = globals()[f"encode_{extension[1:]}"]

    # - Write config

    with open(filename, "w") as f:
        f.write(encoder(config))


# see test_read_and_write_config_file.py for test
