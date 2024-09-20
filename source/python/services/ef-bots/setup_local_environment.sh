# - Go to the service directory

cd ${0%/*}

# - Deactivate virtualenv if active

deactivate

# - Install uv globally if not installed

uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# - Sync uv

uv sync

echo "Installed local environment to .venv/ directory"