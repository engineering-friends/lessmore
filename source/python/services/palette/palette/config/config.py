from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # - OpenAI

    openai_api_key: str

    # - Langchain

    langchain_api_key: str

    # - Telegram

    telegram_bot_token: str
    telegram_test_chat_id: int
