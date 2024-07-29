# - Go to the service directory

cd ${0%/*}
git pull
poetry install --no-root

# Get directories

SERVICE_PATH=$(pwd)
MONOREPO_PATH=$SERVICE_PATH/../../../..

# - Decrypt secrets

$MONOREPO_PATH/git_secret/decrypt_secrets.sh

# - Set PYTHONPATH

export PYTHONPATH="$SERVICE_PATH:$PYTHONPATH"
export PYTHONPATH="$MONOREPO_PATH/source/python/libs/lessmore.utils:$PYTHONPATH"

# - Run the service

poetry run python discord_to_telegram_forwarder/run.py --env prod
#screen -dmS discord_to_telegram_forwarder_prod  -L -Logfile logs/prod.log poetry run python discord_to_telegram_forwarder/run.py --env prod