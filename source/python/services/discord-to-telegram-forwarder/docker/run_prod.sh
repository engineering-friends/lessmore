docker stop discord-to-telegram-forwarder
docker rm discord-to-telegram-forwarder
docker run --detach --pull always --name discord-to-telegram-forwarder marklidenberg/discord-to-telegram-forwarder:latest python /monorepo/source/python/services/discord-to-telegram-forwarder/discord_to_telegram_forwarder/run.py --env prod
