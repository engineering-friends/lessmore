from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # - Telegram

    telegram_api_id: str
    telegram_api_hash: str
    telegram_bot_name: str
    telegram_bot_token: str

    telegram_discussion_group: int

    # - Notion

    notion_token: str
