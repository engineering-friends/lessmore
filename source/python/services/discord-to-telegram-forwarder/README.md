# discord-to-telegram-forwarder

Пересылает посты из дискорда в телеграм 

## Установка

- Установить poetry окружение: `poetry install`
- Добавить конфигурационные файлы: `discord_to_telegram_forwarder/config.secrects.prod.yaml` и `discord_to_telegram_forwarder/config.secrets.test.yaml`

Либо собрать их по шаблонам (`discord_to_telegram_forwarder/config.secrects.prod.yaml.template` и `discord_to_telegram_forwarder/config.secrets.test.yaml.template`), либо попросить файлы конфига у админа. 

- Запустить: `./source/python/services/discord-to-telegram-forwarder/run.sh`