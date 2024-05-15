# - Go to the service directory

cd ${0%/*}
git pull
poetry install

# Get directories

SERVICE_PATH=$(pwd)
MONOREPO_PATH=$SERVICE_PATH/../../../..

# - Decrypt secrets

$MONOREPO_PATH/git_secret/decrypt_secrets.sh

# - Set PYTHONPATH

export PYTHONPATH="$SERVICE_PATH:$PYTHONPATH"
export PYTHONPATH="$MONOREPO_PATH/source/python/libs/lessmore.utils:$PYTHONPATH"

# - Run the service

screen -dmSL discord_to_telegram_forwarder_test poetry run python discord_to_telegram_forwarder/main.py --env prod