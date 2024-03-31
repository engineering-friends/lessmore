from pydantic import BaseSettings


class Config(BaseSettings):
    # - Mi cloud

    mi_cloud_username: str
    mi_cloud_password: str
