import toml
import subprocess
import os


def release():
    # - Load pyproject.toml

    with open('pyproject.toml', 'r') as file:
        pyproject = toml.load(file)

    # - Get current commit hash

    commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()

    # - Get libs dir

    repo_dir = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('utf-8').strip()
    libs_dir = os.path.join(repo_dir, 'source/python/libs')
    lib_paths = [name for name in os.listdir(libs_dir) if os.path.isdir(os.path.join(libs_dir, name))]
    lib_paths = [lib_path for lib_path in lib_paths if not lib_path.startswith('__')] # remove __pycache__ and maybe other system dirs

    # - Add or update libs

    dependencies = pyproject['tool']['poetry']['dependencies']
    for lib_path in lib_paths:
        dependencies[lib_path] = {
            'git': 'https://github.com/engineering-friends/lessmore.git',
            'rev': commit_hash,
            'subdirectory': lib_path
        }

    # - Remove missing libs

    libs_to_remove = set(dependencies.keys()) - set(lib_paths)

    for lib_path in libs_to_remove:
        if 'git' in dependencies[lib_path]:
            del dependencies[lib_path]

    # - Save pyproject.toml

    with open('pyproject.toml', 'w') as file:
        toml.dump(pyproject, file)

    print(f"Updated pyproject.toml with commit hash {commit_hash} and libs: {lib_paths}")

if __name__ == '__main__':
    release()

