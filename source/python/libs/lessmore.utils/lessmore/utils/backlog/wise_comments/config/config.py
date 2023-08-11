import os

from lessmore.utils.load_pydantic_settings import load_config_source


config = read_config(
    config_source=[
        {
            "type": "file",
            "is_required": False,
            "value": "{root}/config.yaml",
        },
        {
            "type": "file",
            "is_required": False,
            "value": "{root}/config.local.yaml",
        },
        {
            "type": "environment_variables",
            "prefix": "WISE_COMMENTS__",
        },
    ],
    context={
        "root": os.path.dirname(__file__),
    },
)

if __name__ == "__main__":
    print(config)
