# - Go to the script directory

cd ${0%/*}

# - Init git secret if not already done

git secret init

# - If there are already gpg keys imported then exit. Check that AE448D555EF175712DBBBFCCABF36667ED4DED6E key is imported with gpg --list-keys

#[keyboxd]
#---------
#pub   ed25519 2024-06-16 [SC]
#      AE448D555EF175712DBBBFCCABF36667ED4DED6E
#uid           [ unknown] Mark Lidenberg <marklidenberg@gmail.com>
#sub   cv25519 2024-06-16 [E]

if gpg --list-keys | grep -q AE448D555EF175712DBBBFCCABF36667ED4DED6E; then
    echo "GPG keys already imported"
    exit 0
fi

# - Get the keys from enrcyped file. Ask admin for the password

unzip gpg_keys.zip
mv gpg_keys/* .
rm -rf gpg_keys

# - Import keys

gpg --import my_public_key.asc
gpg --import my_private_key.gpg

# - Remove keys

rm my_public_key.asc
rm my_private_key.gpg
