# Bump version and set lessmore dependencies to the current commit

# - Go to script directory

cd ${0%/*}

# - Exit if not on master branch

git rev-parse --abbrev-ref HEAD | grep '^master$' > /dev/null || { echo "Current branch is not 'master'. Exiting."; exit 1; }

# - Exit if there are staged changes

git diff --cached --name-only | grep -q . && { echo "There are staged changes. Exiting."; exit 1; }

# - Exit if there are unpulled commits

git fetch origin && git diff --quiet HEAD origin/master ||  { echo "There are some unpulled commits. Exiting."; exit 1; }

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
VERSION=$( poetry version --short )

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
    lib_commited_at=$(TZ=UTC0 git show --quiet --date='format-local:%Y-%m-%d %H:%M:%S' --format="%cd")

    # - Add dependencies in pyproject.toml

    # format: "lessmore.utils" = {git = "https://github.com/engineering-friends/lessmore.git", rev = "...", subdirectory = "source/python/libs/lessmore.utils"} # commited_at: "2024-06-16 15:12:39"
    echo "\"$lib_name\" = {git = \"$lib_git_url\", rev = \"$lib_rev\", subdirectory = \"$lib_subdirectory\"} # commited_at: \"$lib_commited_at\"" >> pyproject.toml

done

# - Commit and push

git add pyproject.toml
git commit --message "chore($project_name): release-$VERSION"
git push