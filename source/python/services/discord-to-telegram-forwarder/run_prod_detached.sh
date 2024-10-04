# - Go to the service directory

cd ${0%/*}
git pull
poetry install --no-root

# Get directories

SERVICE_PATH=$(pwd)
MONOREPO_PATH=$SERVICE_PATH/../../../..

# - Decrypt secrets

bash $MONOREPO_PATH/git_secret/decrypt_secrets.sh

# - Set PYTHONPATH

export PYTHONPATH="$SERVICE_PATH:$PYTHONPATH"
export PYTHONPATH="$MONOREPO_PATH/source/python/libs/lessmore.utils:$PYTHONPATH"

# - Run the service

screen -X -S discord_to_telegram_forwarder_prod quit
screen -S discord_to_telegram_forwarder_prod -L -Logfile logs/prod.log bash -c "uv run python discord_to_telegram_forwarder/run.py --env prod || (echo \"Python script failed. Press any key to continue...\" && read -n 1)"   # `ctrl+a d` to detach