"""Combo Formatter, alpha version. Configures Wise and Black/Rust together in the IDE."""

import os

import typer

from lessmore.utils.file_primitives.list_files import list_files
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config
from lessmore.utils.system.run_system_command import run_system_command
from loguru import logger


config = read_config(
    source=os.path.join(os.path.dirname(__file__), "config.yaml"),
)


def format_file(filename: str) -> None:
    # - Get file type

    if os.path.basename(filename).startswith("."):
        file_type = os.path.basename(filename)
    elif "Dockerfile" in filename:
        file_type = "Dockerfile"
    else:
        file_type = os.path.splitext(filename)[-1]

    logger.debug("Formatting file", filename=filename, file_type=file_type)

    # - Apply formatters

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
            run_system_command(
                command=formatter["command"].format(filename=filename),
                working_dir=formatter.get("working_dir"),
            )


def main(sources: list[str]) -> None:
    assert len(sources) > 0, "Specify sources"
    for source in sources:
        for filename in list_files(source):
            format_file(filename)


if __name__ == "__main__":
    setup_json_loguru()
    typer.run(main)
