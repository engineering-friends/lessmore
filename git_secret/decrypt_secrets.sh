# Decrypt of *.secret files in the repository. This will create the decrypted files in the same directory with the same name but without the .secret extension.

# - Go to repo root

cd ${0%/*}/..

# - Find all git secret files and decrypt them
git secret reveal -fF # -f: force overwrite, -F: continue to reveal even if the file fails to decrypt (usually due to a missing .secret file)