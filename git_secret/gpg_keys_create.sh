# - Go to the script directory

cd ${0%/*}


# - Generate gpg key

gpg --full-generate-key

# - Find ID of generated key and export it to my_public_key.asc, my_private_key.gpg

mkdir gpg_keys
key_id=$(gpg --list-keys --with-colons | awk -F: '/^pub:/ {print $5}')
gpg --export --armor $key_id > gpg_keys/my_public_key.asc
gpg --export-secret-keys --armor $key_id > gpg_keys/my_private_key.gpg

# - Zip

zip -r -e gpg_keys.zip gpg_keys/ # -r for recursive, -e for encryption
rm -rf gpg_keys/

# - Remove gpg key

gpg --delete-secret-keys $key_id
gpg --delete-keys $key_id