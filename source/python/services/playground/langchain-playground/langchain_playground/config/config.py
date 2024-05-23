from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # - OpenAI

    openai_api_key: str

    # - Langchain

    langchain_api_key: str
