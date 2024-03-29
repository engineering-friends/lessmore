#!/usr/bin/env bash

docker build --file Dockerfile --tag "marklidenberg/discord-to-telegram-forwarder:latest" --platform "linux/arm64" ../../../../../ || exit 1
docker push marklidenberg/discord-to-telegram-forwarder:latest