# build docker image with custom context path
BUILDKIT_PROGRESS=plain docker build -t localhost/discord-to-telegram-forwarder:latest -f Dockerfile $LESSMORE_MONOREPO_PATH

# run docker container,
docker run --rm --name discord-to-telegram-forwarder localhost/discord-to-telegram-forwarder:latest python /monorepo/source/python/services/discord-to-telegram-forwarder/discord_to_telegram_forwarder/main.py