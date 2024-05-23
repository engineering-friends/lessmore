"""Print export ready environment variables from file
Example: .env: FOO1 = BAR1... -> FOO1=BAR1 FOO2=BAR2
"""
import fire
import pydantic.config

from deeplay.utils.reflexion import load_module


def get_config(path, config_instance_name: str = "config"):
    """
    :param path: path_to_config_instance
    """

    # - Get config instance

    config = getattr(load_module(path), config_instance_name)
    assert isinstance(config, pydantic.BaseSettings)

    # - Format and return

    return dict(config)


def export_config_envs(path, config_instance_name: str = "config"):
    print("{}".format(" ".join([f"{k.upper()}={str(v)}" for k, v in get_config(path, config_instance_name).items()])))


if __name__ == "__main__":
    fire.Fire(export_config_envs)
