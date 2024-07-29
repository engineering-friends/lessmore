import os

from lessmore.utils.read_config.read_config import read_config


config = read_config(
    source=[
        {"root": os.path.dirname(__file__)},
        "{{root}}/config.yaml",
    ]
)

if __name__ == "__main__":
    print(config)
