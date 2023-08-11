import importlib
import re

from loguru import logger
from pymaybe import maybe

from lessmore.utils.fp import flatten, mark_ends, pairwise
from lessmore.utils.optimize_imports.shorten_imports.parse_from_statement import parse_from_statement


def iterate_import_from(import_from):
    """ "pandas.io.sql" -> ["pandas", "pandas.io", "pandas.io.sql"]"""
    import_from_parts = import_from.split(".")
    for i in range(len(import_from_parts)):
        import_from_part = ".".join(import_from_parts[: i + 1])
        yield import_from_part


assert list(iterate_import_from("pandas.io.sql")) == ["pandas", "pandas.io", "pandas.io.sql"]

"""

!!!DEPRECATED!!!

Shortening imports can break code due to circular imports.

"""


def shorten_imports(text):
    logger.debug("Input text", text=text)

    # - Parse from statements

    from_statements = []

    # case without brackets
    from_statements += re.findall(r"(^from\s+[^\s]+\s+import\s+[^\n\(\)]+\n)", string=text, flags=re.MULTILINE)

    # case with brackets
    from_statements += re.findall(r"(^from\s+[^\s]+\s+import\s+\(*[^\(\)]*\))", string=text, flags=re.MULTILINE)

    logger.debug("from_statements", from_statements=from_statements)

    for from_statement in from_statements:

        if "#" in from_statement:

            # skip commented out imports
            continue

        new_from_statement = ""

        # - Collect new from_statement

        for module_name, value, alias in parse_from_statement(from_statement):
            value_alias = f"{value} as {alias}" if alias else value

            # "pandas.io.sql", "read_sql", "read_sql_alias"
            if value == "*":
                new_import_line = f"from {module_name} import *"

            # try to find shorter version

            for is_first, is_last, module_name_short in mark_ends(iterate_import_from(module_name)):
                logger.debug(
                    "Trying",
                    is_first=is_first,
                    is_last=is_last,
                    module_short=module_name_short,
                    value=value,
                    alias=alias,
                )

                # [(True, False, 'pandas'), (False, False, 'pandas.io'), (False, True, 'pandas.io.sql')]
                try:
                    module_shorter = importlib.import_module(module_name_short)
                    module = importlib.import_module(module_name)

                    if (
                        not is_last
                        and hasattr(module_shorter, value)
                        and getattr(module_shorter, value, None) == getattr(module, value, None)
                    ):

                        # found shorter version!
                        logger.debug("Found shorter version", module_short=module_name_short, value=value, alias=alias)
                        new_import_line = f"from {module_name_short} import {value_alias}"
                        break
                    elif is_last:

                        logger.debug(
                            "Failed to find shorter version", module_short=module_name_short, value=value, alias=alias
                        )

                        # not found shorter version, use longer version
                        new_import_line = f"from {module_name} import {value_alias}"
                        break

                except ModuleNotFoundError:
                    new_import_line = f"from {module_name} import {value_alias}"

            new_from_statement += new_import_line + "\n"

        # - Replace old from statement with new from statement

        text = text.replace(from_statement, new_from_statement)

    return text


def test():
    text = """

Some other text

from pandas.io import *
from pandas.io.sql import read_sql
from pandas.io.sql import read_sql as read_sql_alias
from pandas.io.sql import read_sql, read_sql_query
from pandas.io.sql import (
    read_sql,
    read_sql_query as read_sql_query_alias,
)
from pandas.io.sql import read_sql # commented blocks are not shortened, really

Some other text 
    """
    print(shorten_imports(text))


if __name__ == "__main__":
    from lessmore.utils.loguru_utils import configure_loguru

    configure_loguru(level="debug")

    print(
        shorten_imports(
            """from pyflink_etl.aqueduct import create_aqueduct_consumer_config, create_aqueduct_producer_config
from pyflink_etl.colluder_gun import Alert, BugType, Error
from pyflink_etl.colluder_gun.messages import Participant
from pyflink_etl.colluder_gun.pipelines.pattern_pipeline.enrichment.get_extra_player_id_properties_by_pid import (
    get_extra_player_id_properties_by_pid,
)
from pyflink_etl.colluder_gun.pipelines.pattern_pipeline.enrichment.get_replay_url_from_ultron import (
    get_replay_url_from_ultron,
)
from pyflink_etl.colluder_gun.pipelines.pattern_pipeline.processing.postprocess_player_games import (
    postprocess_player_games,
)
from pyflink_etl.colluder_gun.processing import deserialize_proto, serialize_proto, unfold_kafka_message
"""
        )
    )
