from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # - OpenAI

    openai_api_key: str

    # - Langchain

    langchain_api_key: str

    # - Notion

    notion_token: str
    notion_test_page_id: str

    # - Imgur

    imgur_client_id: str
    imgur_client_secret: str

    # - Yandex disk

    yandex_disk_token: str
