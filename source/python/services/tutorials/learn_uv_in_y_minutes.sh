# - Install uv

curl -LsSf https://astral.sh/uv/install.sh | sh

# - Pip

# These commands work directly with the virtual environment, in contrast to uv's primary interfaces where the virtual environment is managed automatically

# -- Install package with pip

uv venv
uv pip install ruff
source .venv/bin/activate
ruff --version
uv pip freeze
uv pip check # It is possible to install packages with conflicting requirements into an environment if installed in multiple steps, this checks the conflicts
deactivate
rm -rf .venv

# -- Install to specific python environment

#uv pip install --python /path/to/python

# -- Install from requirements.txt

# uv pip install -r requirements.in
# uv pip install -r requirements.txt
# uv pip install -r pyproject.toml

# - Project management


# -- Create project

uv init example --no-workspace
cd example
uv add ruff # will create .venv/ and install ruff
uv run ruff check # "All checks passed!"
cd ..
rm -rf example

# - Pythons


# -- Install pythons (pyenv alternative)

uv python install 3.10 3.11 3.12 #  ~/.local/share/uv/python/cpython-3.12.0-macos-aarch64-none/bin/python3
uv python list

# -- Run python locally (local .venv)

uv run --python pypy@3.8 -- python --version
#uv venv --python 3.12.0 # run python in the virtual environment

# -- Pin python to the directory

uv python pin pypy@3.11 # creates `.python-version` file
rm .python-version

# - Scripts

echo 'import requests; print(requests.get("https://astral.sh"))' > example.py

uv add --script example.py requests # will create virtualenv in some temporary directory

uv run example.py # will create virtualenv and install requests

# virtualenv is created in /tmp/uv/example.py/venv

rm example.py # clean up

# - Script

# -- Example 1

echo 'import requests; import sys; print(sys.executable)' > example.py
uv run --with requests example.py
rm example.py

 # -- Example 2

echo 'import requests; import sys; print(sys.executable)' > example.py
uv add --script example.py requests # will add dependencies header to example.py
uv run --no-project example.py # will create virtualenv and install requests (in some temporary directory, e.g. ~.cache/uv/archive-v0/LSz98Yb91wFCRf3Af8fDQ/bin/python3)
rm example.py

# - Tools


# -- Run ephemeral env

uvx pycowsay 'hello world!'

# -- Install

uv tool install pycowsay
pycowsay 'hello world!'