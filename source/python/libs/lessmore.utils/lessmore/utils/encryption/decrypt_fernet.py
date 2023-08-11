import base64

import cryptography.fernet

from lessmore.utils.encryption.encrypt_fernet import encrypt_with_fernet
from lessmore.utils.encryption.hash_argon import hash_with_argon


def decrypt_with_fernet(value: bytes, secret: str):

    # - Create Fernet encryptor

    encryptor = cryptography.fernet.Fernet(secret)

    # - Encrypt value

    return encryptor.decrypt(value)


def test():
    value = encrypt_with_fernet(
        value=b"foo",
        secret="WpZ5qbdLSxcIoG5HdR28dsdjbpJ12UUpRsH9bA9-nrM=",  # pragma: allowlist secret
    )
    assert (
        decrypt_with_fernet(
            value,
            secret="WpZ5qbdLSxcIoG5HdR28dsdjbpJ12UUpRsH9bA9-nrM=",  # pragma: allowlist secret
        )
        == b"foo"
    )


if __name__ == "__main__":
    test()
