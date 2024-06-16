# Quickstart
Run `gpg_keys_imports.sh` and then `decrypt_secrets.sh`. Now you have access to all secret files in the repo

# gpg keys

- Master gpg keys are stored in encrypted `.zip` file `gpg_keys.zip`
- `gpg_keys_imports.sh` imports keys from `gpg_keys.zip` to your gpg keychain
- `gpg_keys_create.sh` creates new gpg keys and adds them to `gpg_keys.zip`

# Secrets 

- Secrets are stored in `.secret` files
- `decrypt_secrets.sh` decrypts all `.secret` files and put their contents into files without `.secret` suffix
- `encrypt_secrets.sh` goes through all `.secret` files and if corresponding file without `.secret` suffix exists, encrypts it into `.secret` file
- To create a secret, copy your file to a new file with `.secret` extension and run `encrypt_secrets.sh`
- To delete a secret, delete `.secret` file