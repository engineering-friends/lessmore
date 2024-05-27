from telegram_poweruser.imports.external import *


# - Globals


class Config(BaseSettings):
    session_folder_title: str = "💬 now"
    is_initialized: bool = False
    session_period: str = "1h"
    monitoring_channel_name: str = "Channeled Sharing Monitoring"


# - Load config

config = Config()  # note for dima: set default config values in the class definition
