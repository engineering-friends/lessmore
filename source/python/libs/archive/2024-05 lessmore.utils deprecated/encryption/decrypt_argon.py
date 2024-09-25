import base64

import cryptography.fernet

from lessmore.utils.encryption.hash_argon import hash_with_argon


def decrypt_with_argon(value: bytes, secret: str):
    # - Generate password hash for fernet

    password_hash = hash_with_argon(secret=secret, salt="*" * 16)  # using default salt

    # - Encode it to base64

    encoded_hash = base64.urlsafe_b64encode(password_hash[-32:].encode())

    # - Create Ferney encryptor

    encryptor = cryptography.fernet.Fernet(encoded_hash)

    # - Encrypt value

    return encryptor.decrypt(value)


def test():
    print(
        decrypt_with_argon(
            value=b"gAAAAABkv-nwXy-Py0nJHEg5m6oX2G9dKRSrgXu53XZrUgyrSvQ5hdX2UNClkBMf474BOzShm-WTq7mV_HUBjrqPij10Hz-HSg==",  # pragma: allowlist secret
            secret="my_password",  # pragma: allowlist secret
        )
    )


if __name__ == "__main__":
    test()
