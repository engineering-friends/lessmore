
# - Got to the root of the repository

cd ${0%/*}/..

# - Find all .secret files and add them to the git secret

find . -type f -name "*.secret" | while read -r filename; do
  echo "Adding secret :${filename%.secret}"
  git secret add "${filename%.secret}"
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

