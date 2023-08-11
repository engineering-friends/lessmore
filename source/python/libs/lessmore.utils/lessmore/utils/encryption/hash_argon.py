import os

from typing import Optional, Union

import argon2

from argon2.low_level import hash_secret

from lessmore.utils.unified import to_bytes


def hash_with_argon(secret: Union[bytes, str], salt: Union[bytes, str]):
    # - Use hash_secret directly to pass custom salt (password_hasher.hash() uses the same hash_secret call, but with random salt)

    password_hasher = argon2.PasswordHasher()

    return hash_secret(
        secret=to_bytes(secret),
        salt=to_bytes(salt) or os.urandom(password_hasher.salt_len),
        time_cost=password_hasher.time_cost,
        memory_cost=password_hasher.memory_cost,
        parallelism=password_hasher.parallelism,
        hash_len=password_hasher.hash_len,
        type=password_hasher.type,
    ).decode()


def test():
    print(hash_with_argon("my_password", "my_salt" * 3))


if __name__ == "__main__":
    test()
