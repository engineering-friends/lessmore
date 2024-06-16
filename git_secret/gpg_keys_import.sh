# - Go to the script directory

cd ${0%/*}

# - Init git secret if not already done

git secret init

# - If there are already gpg keys imported then exit. Check that F123DBA179C7A29B79F1596352BD4E130D6980FA key is imported with gpg --list-keys

#[keyboxd]
#---------
#pub   ed25519 2023-08-11 [SC]
#      F123DBA179C7A29B79F1596352BD4E130D6980FA
#uid           [ unknown] Mark Lidenberg (lessmore-repo) <marklidenberg@gmail.com>
#sub   cv25519 2023-08-11 [E]

if gpg --list-keys | grep -q F123DBA179C7A29B79F1596352BD4E130D6980FA; then
    echo "GPG keys already imported"
    exit 0
fi

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
