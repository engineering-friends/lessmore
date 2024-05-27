from telegram_poweruser.imports.external import *


class Config(BaseSettings):
    topics_database_id: str = "0b0b4d4c2f934e6787ac6f633848e702"
    folder_title: str = "🗣️"
    channel_name_prefix: str = "#topic: "
    channels_property_name: str = "Люди и коммьюнити"
    telegram_property_name: str = "Telegram"
    probability_property_name: str = "Вероятность"
    called_name_property_name: str = "Назывное имя"
    name_property_name: str = "Имя"


config = Config()  # note for dima: set default config values in the class definition

if __name__ == "__main__":
    print(config.topics_database_id)
