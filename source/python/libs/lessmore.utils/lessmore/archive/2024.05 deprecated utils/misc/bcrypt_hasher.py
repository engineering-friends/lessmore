from typing import Union

import bcrypt

from lessmore.utils.to_anything import unified_bytes


class BCryptHasher:
    def hash(self, secret: Union[str, bytes]):
        # - Convert secret to bytes

        secret = unified_bytes.to_bytes(secret)

        # - Calculate hash

        return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("ascii")

    def verify(self, hash, secret):
        # - Convert secret and hash to bytes

        secret = unified_bytes.to_bytes(secret)
        hash = unified_bytes.to_bytes(hash)

        # - Verify

        assert bcrypt.checkpw(secret, hash), "Verification failed"


def test():
    hasher = BCryptHasher()
    hash = hasher.hash("my_secret")
    hasher.verify(hash, "my_secret")

    # NOTE: custom salt is not implemented in BCryptHasher


if __name__ == "__main__":
    test()
