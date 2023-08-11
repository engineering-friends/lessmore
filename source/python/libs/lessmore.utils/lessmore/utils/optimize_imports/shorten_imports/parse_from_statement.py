import re

from pymaybe import maybe

from lessmore.utils.fp import flatten, mark_ends, padded, pairwise, unzip, zip_broadcast


def parse_from_statement(from_statement):

    search = re.search(
        r"^from\s+([^\s]+)\s+import\s+([^\n\(\)]+)$", string=from_statement, flags=re.MULTILINE
    ) or re.search(r"^from\s+([^\s]+)\s+import\s+\(*([^\(\)]*)\)$", string=from_statement, flags=re.MULTILINE)

    module_name, values = search.groups()  # ('pandas.io.sql', 'read_sql, read_sql_query')

    # split by line
    values = values.splitlines()

    # split by comma
    values = flatten([value.split(",") for value in values])  # ['read_sql', ' read_sql_query']

    # strip
    values = [import_what.strip() for import_what in values]

    # Remove empty
    values = [import_what for import_what in values if import_what]

    # spilt aliases
    values = [re.split(" [aA][sS] ", value) if " as " in value.lower() else (value, None) for value in values]

    # - Wrap into dicts

    return [[module_name.strip(), value.strip(), maybe(alias).strip().or_else("")] for value, alias in values]


def test():
    print(parse_from_statement("from pandas.io import *"))
    print(parse_from_statement("from pandas.io.sql import read_sql"))
    print(parse_from_statement("from pandas.io.sql import read_sql as read_sql_alias"))
    print(parse_from_statement("from pandas.io.sql import read_sql, read_sql_query"))
    print(
        parse_from_statement(
            """    from pandas.io.sql import (
        read_sql,
        read_sql_query as read_sql_query_alias,
    )""".strip()
        )
    )


if __name__ == "__main__":
    test()
