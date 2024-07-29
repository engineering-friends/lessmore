# discord-to-telegram-forwarder

Forwards messages from Discord to Telegram.

# Установка

- `poetry install`
- Add configs `discord_to_telegram_forwarder/config.secrects.prod.yaml` and `discord_to_telegram_forwarder/config.secrets.test.yaml` from the templates, or get ones from the admin 
- Run `./source/python/services/discord-to-telegram-forwarder/run_test.sh` или `./source/python/services/discord-to-telegram-forwarder/run_prod.sh`

# Деплоймент 

Deployed manually for now, without docker image (it's faster), will do proper CI/CD later.

# Code 

Core functions: 
- `send_discord_post_to_telegram`: sends post from Discord to Telegram
- `update_comments_counter`: updates comments counter in the post

Entry point: `main.py`