from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # - OpenAI

    openai_api_key: str

    # - Langchain

    langchain_api_key: str

    # - Notion

    notion_token: str
    notion_test_page_id: str

    # - Amazon

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str
