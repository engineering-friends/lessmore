from lessmore.utils.to_anything import to_datetime_str


def create_unique_values_sql(
    now,
    table,
    column,
    timestamp_column: str = None,
    values_period=None,
    filter_sql: str = None,
):
    filter_sql = f"AND {filter_sql}" if filter_sql else ""

    return f"""
        '{to_datetime_str(now, like='2020-01-01 00:00:00')}' AS now, --
        subtractDays(toDateTime(now), {values_period}) AS border_at, --
        (SELECT groupArray(DISTINCT {column})
        FROM {table}
        PREWHERE {timestamp_column} >= border_at
        WHERE
            {column} NOT IN (
                SELECT DISTINCT {column}
                FROM {table}
                WHERE {timestamp_column} < border_at
                {filter_sql})
            {filter_sql})
    """


def test():
    print(
        create_unique_values_sql(
            table="network_pppoker_public.hand_history__transformed_from_observer",
            column="TableBigBlind",
            timestamp_column="RowCreatedAt",
            values_period=1,
        )
    )


if __name__ == "__main__":
    test()
