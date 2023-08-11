import os

import fire

from loguru import logger

from lessmore.utils.config import read_config
from lessmore.utils.list_files import list_files
from lessmore.utils.loguru_utils import configure_loguru
from lessmore.utils.system import execute_system_command


config = read_config(
    config_source=[
        {
            "is_required": False,
            "type": "file",
            "value": os.path.join(os.path.dirname(__file__), "config.yaml"),
        },
        {
            "is_required": False,
            "type": "file",
            "value": os.path.join(os.path.dirname(__file__), "config.local.yaml"),
        },
    ]
)


def get_file_type(filename):
    if "Dockerfile" in filename:
        return "Dockerfile"
    else:
        return os.path.splitext(filename)[-1]


def format_file(filename):
    file_type = get_file_type(filename)
    for group, values in config.items():
        if file_type not in values["file_types"]:
            continue

        for formatter in values["formatters"]:
            logger.debug(
                "Running formatter on file",
                formatter=formatter["name"],
                filename=filename,
                command=formatter["command"].format(filename=filename),
            )
            execute_system_command(
                formatter["command"].format(filename=filename), working_directory=formatter.get("working_directory")
            )


def main(*sources):
    assert len(sources) > 0, "Specify sources"
    for source in sources:
        for filename in list_files(source):
            format_file(filename)


if __name__ == "__main__":
    configure_loguru(level="DEBUG")
    fire.Fire(main)
