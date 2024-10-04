# - Go to the service directory

cd ${0%/*}
git pull

# - Install uv if not installed

uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# - Sync uv

uv sync

# Get directories

SERVICE_PATH=$(pwd)
MONOREPO_PATH=$(echo $SERVICE_PATH | sed -E 's/(.*)\/source\/.*/\1/') # Crop /a/b/c/.../lessmore/source/... -> /a/b/c/.../lessmore

# - Decrypt secrets

bash $MONOREPO_PATH/git_secret/decrypt_secrets.sh

# - Set PYTHONPATH

export PYTHONPATH="$SERVICE_PATH:$PYTHONPATH"
export PYTHONPATH="$MONOREPO_PATH/source/python/libs/lessmore.utils:$PYTHONPATH"

# - Run the service

screen -X -S discord_to_telegram_forwarder_test quit
screen -S discord_to_telegram_forwarder_test -L -Logfile logs/prod.log bash -c "uv run python discord_to_telegram_forwarder/run.py --env test || (echo \"Python script failed. Press any key to continue...\" && read -n 1)"   # `ctrl+a d` to detach