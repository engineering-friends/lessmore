import os
import sys

from pathlib import Path
from typing import Literal

from loguru import logger
from second_sun.config.config import Config
from second_sun.deps.deps import Deps

from lessmore.utils.configure_loguru.format_as_json_colored.format_as_json_colored import format_as_json_colored
from lessmore.utils.load_pydantic_settings.load_pydantic_settings import load_pydantic_settings


def init_deps(log_level="DEBUG") -> Deps:
    # - Init config

    config = load_pydantic_settings(
        pydantic_class=Config,
        config_source=[
            {
                "type": "file",
                "is_required": False,
                "value": "{root}/config.secrets.yaml",
            },
            # "environment_variables",
        ],
        context={
            "root": str(Path(__file__).parent / "../config"),
        },
    )

    # - Init logger

    logger.remove()
    logger.add(sink=sys.stdout, level=log_level, format=format_as_json_colored)

    # - Return context

    os.makedirs(str(Path(__file__).parent / "../../data/dynamic"), exist_ok=True)

    return Deps(config=config)
