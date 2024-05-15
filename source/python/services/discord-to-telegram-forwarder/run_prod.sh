cd ${0%/*}
git pull
poetry install
poetry run python discord_to_telegram_forwarder/main.py --env prod