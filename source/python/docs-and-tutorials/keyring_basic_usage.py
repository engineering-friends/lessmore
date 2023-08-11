import json

import keyring


# - Single secret per service-username pair

keyring.set_password(service="my-service", username="username", password="secret")  # pragma: allowlist secret
print(keyring.get_password(service="my-service", username="secret"))

# - Multiple secrets per service-username pair

secrets_json = json.dumps({"secret1": "secret1", "secret2": "secret2"})
keyring.set_password(service="my-service", username="username", password=secrets_json)  # pragma: allowlist secret
print(keyring.get_password(service="my-service", username="secret"))
