from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # - Telegram

    telegram_bot_token: str
    telegram_test_chat_id: int
