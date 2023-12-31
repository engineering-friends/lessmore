import base64

import cryptography.fernet

from lessmore.utils.encryption.hash_argon import hash_with_argon


def encrypt_with_fernet(value: bytes, secret: str):
    # - Create Fernet encryptor

    encryptor = cryptography.fernet.Fernet(secret)

    # - Encrypt value

    return encryptor.encrypt(value)


def test():
    print(
        encrypt_with_fernet(
            value=b"foo",
            secret="WpZ5qbdLSxcIoG5HdR28dsdjbpJ12UUpRsH9bA9-nrM=",  # generated by cryptography.fernet.Fernet.generate_key()  # pragma: allowlist secret
        )
    )


if __name__ == "__main__":
    test()
