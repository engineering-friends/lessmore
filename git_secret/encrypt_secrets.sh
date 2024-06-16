# Encrypts all secrets, e.g. for all pairs `a`, `a.secret` overwrites `a.secret` with the new decrypted content of `a`

# - Got to the root of the repository

cd ${0%/*}/..

# - Find all .secret files and add them to the git secret

find . -type f -name "*.secret" | while read -r filename; do
  echo "Adding secret :${filename%.secret}"

  # - Create a stub file if ${filename%.secret} does not exist

  created_stub=false
  if [ ! -f "${filename%.secret}" ]; then
    touch "${filename%.secret}"
    created_stub=true
  fi

  # - Add the secret to git secret

  git secret add "${filename%.secret}" 2>&1 | grep -v "git-secret: abort: file not found" >&2 # silence the "file not found" error

  # - Remove stub file if it was created by the script

  if [ "$created_stub" = true ]; then
    rm "${filename%.secret}"
  fi

done

# - Find all missing .secret files and remove them from git secret

while IFS= read -r filename
do
  if [ ! -f "$filename.secret" ]; then
    echo "file $filename.secret does not exist. Removing from git secret..."

    # - Create a backup of $filename if it exists

    if [ -f "$filename" ]; then
      mv "$filename" "$filename.bak"
    fi

    # - Create stub files

    touch "$filename"
    touch "$filename.secret"

    # - Remove secret

    git secret remove "$filename"

    # - Remove stub files

    rm "$filename"
    rm "$filename.secret"

    # - Restore the backup of $filename if it exists

    if [ -f "$filename.bak" ]; then
      mv "$filename.bak" "$filename"
    fi

  fi
done <<< "$(git secret list)"

# - Encrypt all secrets in the repository

git secret hide -F # -F forces hide to continue if a file to encrypt is missing. This will create encrypted filenames with the .secret suffix

