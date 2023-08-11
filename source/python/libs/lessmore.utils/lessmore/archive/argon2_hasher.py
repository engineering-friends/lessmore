from typing import Optional, Union

from argon2 import PasswordHasher
from argon2.low_level import hash_secret

from lessmore.utils.to_anything import unified_bytes


class Argon2Hasher(PasswordHasher):
    def hash(self, secret: Union[str, bytes], salt: Optional[Union[str, bytes]] = None):
        # - Convert secret and salt to bytes

        secret = unified_bytes.to_bytes(secret, encoding=self.encoding)
        if salt:
            salt = unified_bytes.to_bytes(salt, encoding=self.encoding)

        # - Calculate hash

        if not salt:
            return super().hash(secret)
        else:
            return hash_secret(
                secret=secret,
                salt=salt,
                time_cost=self.time_cost,
                memory_cost=self.memory_cost,
                parallelism=self.parallelism,
                hash_len=self.hash_len,
                type=self.type,
            ).decode("ascii")

    def verify(self, hash, secret):
        return super().verify(hash=hash, password=secret)


def test():
    hasher = Argon2Hasher()
    hash = hasher.hash("my_secret")
    assert hasher.verify(hash, "my_secret")

    hash = hasher.hash("my_secret", salt="my_salt" * 3)
    assert (
        hash
        == "$argon2id$v=19$m=65536,t=3,p=4$bXlfc2FsdG15X3NhbHRteV9zYWx0$pwiqkv7Qd3SqfH1q7ReGl9A8YDIxmd3bgO/pdFaNiL0"
    )
    assert hasher.verify(hash, "my_secret")


if __name__ == "__main__":
    test()
