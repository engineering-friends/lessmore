import os

from lessmore.utils.coder import (  # NOTE: do not delete, used in globals() method
    decode_env,
    decode_json,
    decode_msgpack,
    decode_yaml,
)


SUPPORTED_EXTENSIONS = [".env", ".json", ".yaml"]


def read_config_file(filename: str) -> dict:
    # - Get extension

    extension = os.path.splitext(filename)[-1]

    assert extension in SUPPORTED_EXTENSIONS, f"Non supported config extension: {extension}"

    # - Get decoder

    decoder = globals()[f"decode_{extension[1:]}"]

    # - Get config contents

    with open(filename) as f:
        contents = f.read()

    # - Decode

    result = decoder(contents)

    return result


# see test_read_and_write_config_file.py for test
