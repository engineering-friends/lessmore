# Bump version and set lessmore dependencies to current commit

# - Go to script directory

cd ${0%/*}

# - Fix project name

# -- Get directory name

dir=$(basename "$(pwd)")

# -- Crop date at the beginning (2024 my_project -> my_project, 2024-06 my_project -> my_project, 2024-06-01 my_project -> my_project)

project_name=$(echo $dir | sed -E 's/^[0-9]{4}(-[0-9]{2}){0,2} //')

# -- Rename project in pyproject.toml

sed -i '' "s/\(name = \"\)[^\"]*\(\".*\)/\1$project_name\2/" pyproject.toml

# - Bump poetry version

# poetry version major
# poetry version minor
poetry version patch

# - Iterate over all <git_root>/source/python/libs/* directories and set dependencies in pyproject.toml for current commits

# -- Get git root
git_root=$(git rev-parse --show-toplevel)

# -- Remove all git dependencies from pyproject.toml starting with lessmore (like "lessmore.utils")

sed -i '' '/lessmore\./d' pyproject.toml

# -- Add dependencies for all libraries in <git_root>/source/python/libs/*

for lib_dir in $(find $git_root/source/python/libs -maxdepth 1 -mindepth 1 -type d); do
    # - Skip __pycache__ directories

    if [[ $lib_dir == *"__pycache__"* ]]; then
        continue
    fi

    # - Get lib name, git url, rev and subdirectory

    lib_name=$(basename $lib_dir)
    lib_git_url="https://github.com/engineering-friends/lessmore.git"
    lib_rev=$(git rev-parse HEAD)
    lib_subdirectory="source/python/libs/$lib_name"

    # - Add dependencies in pyproject.toml

    # format: "lessmore.utils" = {git = "https://github.com/engineering-friends/lessmore.git", rev = "...", subdirectory = "source/python/libs/lessmore.utils"}
    echo "\"$lib_name\" = {git = \"$lib_git_url\", rev = \"$lib_rev\", subdirectory = \"$lib_subdirectory\"}" >> pyproject.toml

done
