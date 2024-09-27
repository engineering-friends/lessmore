import random

from typing import Optional

import coolname
import shortuuid


# todo maybe: make a better id generator [@marklidenberg]


def generate_id(seed: Optional[str] = None):
    if seed:
        random.seed(seed)

    if seed:
        result = coolname.generate_slug(3) + "-" + shortuuid.uuid(seed)[:8]
    else:
        result = coolname.generate_slug(3) + "-" + shortuuid.uuid()[:8]

    if seed:
        random.seed(None)

    return result


def test():
    print(generate_id())
    assert generate_id(seed="test") == "precious-translucent-wasp-FWWdRjfX"


if __name__ == "__main__":
    test()
