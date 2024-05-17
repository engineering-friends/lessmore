docker stop discord-to-telegram-forwarder-test
docker rm discord-to-telegram-forwarder-test
docker run --pull always --name discord-to-telegram-forwarder-test marklidenberg/discord-to-telegram-forwarder:latest python /monorepo/source/python/services/discord-to-telegram-forwarder/discord_to_telegram_forwarder/run.py --env test



