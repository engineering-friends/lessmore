import os.path

from lessmore.utils.apply_recursively import apply_recursively
from lessmore.utils.dictionary import flatten_nested


def _inflate_envs(envs_by_name: dict, separator: str = "__", to_upper_case: bool = True) -> None:
    # - Flatten nested

    envs_by_name = flatten_nested(envs_by_name, separator=separator)

    # - To upper case if needed

    if to_upper_case:
        envs_by_name = {k.upper(): v for k, v in envs_by_name.items()}

    # - Stringify

    envs_by_name = apply_recursively(value=envs_by_name, value_func=str)

    # - Inflate values

    for env_name, env in envs_by_name.items():
        os.environ[env_name] = env


def test():
    _inflate_envs(envs_by_name={"a": {"b": "c"}})
    assert os.environ["A__B"] == "c"


if __name__ == "__main__":
    test()
