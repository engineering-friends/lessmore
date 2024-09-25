import base64
import json

import cryptography.fernet

from lessmore.utils.encryption.hash_argon import hash_with_argon


def encrypt_with_argon(value: bytes, secret: str):
    # - Generate password hash for fernet

    password_hash = hash_with_argon(secret=secret, salt="*" * 16)  # using default salt

    # - Encode it to base64

    encoded_hash = base64.urlsafe_b64encode(password_hash[-32:].encode())

    # - Create Fernet encryptor

    encryptor = cryptography.fernet.Fernet(encoded_hash)

    # - Encrypt value

    return encryptor.encrypt(value)


def test():
    value = {"poker_network": "PMTR", "game_id": "95978811-46", "observer_player_ids": ["asdfasdfasdf"]}
    print(encrypt_with_argon(value=json.dumps("value").encode(), secret="my_password"))  # pragma: allowlist secret


if __name__ == "__main__":
    test()
