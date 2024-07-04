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

    # iam -> create user -> add access key + enable ACL in the bucket + enable public + public policy: {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::lessmore/*"}]}
    bucket: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str
