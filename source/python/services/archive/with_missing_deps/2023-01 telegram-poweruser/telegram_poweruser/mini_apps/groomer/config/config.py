from telegram_poweruser.imports.external import *


# - Globals


class Config(BaseSettings):
    session_folder_title: str = "Сессии"
    ping_sticker_set: str = "Hug your friends"
    ping_sticker_document_ids_json: str = "[19430492176646423, 19430492176646441, 19430492176646443, 19430492176646422, 19430492176646427, 19430492176646429]"
    monitoring_channel_peer_id: int = 651693208  # "Channeled Sharing Monitoring"

    ping_periods_json: str = '["1d", "3d", "7d", "14d", "28d", "56d", "112d", "365d", "700d"]'
    dialogs_period: str = "10m"

    @property
    def ping_sticker_document_ids(self):
        return json.loads(self.ping_sticker_document_ids_json)

    @property
    def monitoring_channel_peer(self):
        return types.InputPeerChat(chat_id=self.monitoring_channel_peer_id)

    @property
    def ping_periods(self):
        return json.loads(self.ping_periods_json)


# - Load config

config = Config()  # note for dima: set default config values in the class definition
