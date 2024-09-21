# Decrypts all secrets, e.g. for all `a.secret` files, it creates a `a` file with the decrypted content.

# - Go to repo root

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

    # - Create a directory if it does not exist

    mkdir -p "$(dirname "$filename")"

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


# - Find all git secret files and decrypt them

git secret reveal -fF # -f: force overwrite, -F: continue to reveal even if the file fails to decrypt (usually due to a missing .secret file)