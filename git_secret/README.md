# Secrets 

- Secrets are all `.secret` files
- `decrypt_secrets.sh` decrypts all `.secret` files and put them in the same directory
- `encrypt_secrets.sh` goes over all `.secret` files without suffix `.secret` and encrypt them into `.secret` files
- `decrypt_secrets.sh` and `encrypt_secrets.sh` keep all `git-secret` catalog in sync with `.secret` files 
- To create a secret, copy your file to a new file with `.secret` extension and run `encrypt_secrets.sh`
- To delete a secret, delete `.secret` file

# gpg keys

- Master gpg keys are stored in encrypted `gpg_keys.zip` file
- `gpg_keys_imports.sh` imports keys from `gpg_keys.zip` to your gpg keychain
- `gpg_keys_create.sh` creates new gpg keys and adds them to `gpg_keys.zip`