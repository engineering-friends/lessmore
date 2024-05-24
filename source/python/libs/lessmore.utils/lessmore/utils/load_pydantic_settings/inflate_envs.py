import os.path

from lessmore.utils.apply import apply


def inflate_envs(envs_by_name: dict, to_upper_case: bool = True) -> None:
    # - To upper case if needed

    if to_upper_case:
        envs_by_name = {k.upper(): v for k, v in envs_by_name.items()}

    # - Stringify

    envs_by_name = apply(value=envs_by_name, value_func=str)

    # - Inflate values

    for env_name, env in envs_by_name.items():
        os.environ[env_name] = env


def test():
    inflate_envs(envs_by_name={"a": "b"})
    assert os.environ["A"] == "b"


if __name__ == "__main__":
    # test()
    import anyconfig

    print(anyconfig.load("config.yaml"))
