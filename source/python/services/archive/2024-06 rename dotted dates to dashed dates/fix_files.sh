#!/bin/bash

# - Go to scripts directory

cd ${0%/*}

# - Rename recursively

rename_recursively() {
    local dir="$1"

    # Find all files and directories, sorted by depth to avoid issues with renaming parent directories
    find "$dir" -depth -name "*.*" | while IFS= read -r path; do
        # Get the directory and the base name of the current path
        dir=$(dirname "$path")
        base=$(basename "$path")

        # Replace dots in the date format with dashes
        new_base=$(echo "$base" | sed -E 's/([0-9]{4})\.([0-9]{2})(\.([0-9]{2}))?/\1-\2\4/')

        # Rename the file or directory if the name has changed
        if [[ "$base" != "$new_base" ]]; then
            mv "$dir/$base" "$dir/$new_base"
        fi
    done
}

rename_recursively "."
