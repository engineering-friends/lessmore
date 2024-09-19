from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # - Notion

    notion_token: str
