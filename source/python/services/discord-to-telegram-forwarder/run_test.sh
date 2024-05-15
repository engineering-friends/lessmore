# - Go to the service directory

cd ${0%/*}
git pull
poetry install

# - Decrypt secrets

./../../../../git_secret/decrypt_secrets.sh


# Get the current directory

CURRENT_DIR=$(pwd)

# Check if the current directory is in PYTHONPATH
if [[ ":$PYTHONPATH:" != *":$CURRENT_DIR:"* ]]; then
    export PYTHONPATH="$CURRENT_DIR:$PYTHONPATH"
fi

# - Run the service

poetry run python discord_to_telegram_forwarder/main.py --env test