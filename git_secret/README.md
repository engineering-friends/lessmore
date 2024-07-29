# Quickstart
To gain access to the repository secrets, you need the master password. Obtain it from the admin.

Once you have the master password, execute `gpg_keys_imports.sh` followed by `decrypt_secrets.sh`. You will then have access to all secret files in the repository.

# Usage

- Secrets are stored in `.secret` files.
- `decrypt_secrets.sh` decrypts all `.secret` files and outputs their contents into corresponding files without the `.secret` suffix (e.g., `config.yaml.secret` becomes `config.yaml`).
- `encrypt_secrets.sh` processes all `.secret` files and, if a corresponding file without the `.secret` suffix exists, encrypts it back into a `.secret` file (e.g., `config.yaml` becomes `config.yaml.secret`).
- To create a secret, copy your file to a new file with the `.secret` extension and run `encrypt_secrets.sh`.
- To delete a secret, simply delete the `.secret` file.

# How are GPG keys managed?

- Master GPG keys are stored in an encrypted `.zip` file named `gpg_keys.zip`.
- `gpg_keys_imports.sh` imports keys from `gpg_keys.zip` into your GPG keychain.
- `gpg_keys_create.sh` creates new GPG keys and adds them to `gpg_keys.zip`.
