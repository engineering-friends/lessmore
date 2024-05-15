# - Go to the service directory

cd ${0%/*}
git pull
poetry install

# - Decrypt secrets

./../../../../git_secret/decrypt_secrets.sh

# - Run the service

poetry run python discord_to_telegram_forwarder/main.py --env prod