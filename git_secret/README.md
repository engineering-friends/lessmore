# gpg keys

- Master gpg keys are stored in encrypted .zip file gpg_keys.zip
- You can import them with `gpg_keys_imports.sh`
- You can create your own gpg keys with `gpg_keys_create.sh`

# Secrets 

- Secrets are all .secret files
- `decrypt_secrets.sh` will decrypt all `.secret` files and put them in the same directory
- `encrypt_secrets.sh` will go over all `.secret` files and encrypt encrypt files that exist in the same directory
- `decrypt_secrets.sh` and `encrypt_secrets.sh` keep all git-secret secrets in sync with `.secret` files 
- To create a secret, copy your file to a new file with `.secret` extension and run `encrypt_secrets.sh`
- To delete a secret, just delete `.secret` file.