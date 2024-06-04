# - Go to the script directory

cd ${0%/*}

# - Init git secret if not already done

git secret init

# - Get the keys from enrcyped file. Ask admin for the password

unzip files/gpg_keys.zip
mv gpg_keys/* .
rm -rf gpg_keys

# - Import keys

gpg --import my_public_key.asc
gpg --import my_private_key.gpg

# - Remove keys

rm my_public_key.asc
rm my_private_key.gpg
