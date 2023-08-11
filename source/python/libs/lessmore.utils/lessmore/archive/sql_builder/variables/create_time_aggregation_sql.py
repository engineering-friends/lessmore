from datetime import datetime

from lessmore.utils.to_anything import to_datetime_str


def create_time_aggregation_sql(
    now: datetime,
    table: str,
    aggregation: str,
    timestamp_column: str,
    period_days: int,
    period_lag_days: int = 0,
    start_at_first_timestamp: bool = False,
    stop_at_last_timestamp: bool = False,
    divide_by_days_in_period: bool = False,
):
    return f"""
      toDateTime('{to_datetime_str(now, like='2020-01-01 00:00:00')}') AS now, --
      (SELECT min({timestamp_column}) FROM {table}) AS first_timestamp, --
      (SELECT max({timestamp_column}) FROM {table}) AS last_timestamp, --
      {"last_timestamp" if stop_at_last_timestamp else "now"}{"" if not period_lag_days else f" - INTERVAL {period_lag_days} DAY"} AS stop_at, --
      {"greatest(first_timestamp, stop_at - INTERVAL {} DAY)".format(period_days) if start_at_first_timestamp else "stop_at - INTERVAL {} DAY".format(period_days)} AS start_at, --
      (
      SELECT
          {aggregation}{"" if not divide_by_days_in_period else "/ ((stop_at - start_at) / (24 * 60 * 60))"}
        FROM
            {table}
            PREWHERE
            {timestamp_column} >= start_at and {timestamp_column} <= stop_at
      )
""".strip()


def test():
    print(
        create_time_aggregation_sql(
            now=datetime.now(),
            aggregation="count(StartedDateTime)",
            table="orrr.games",
            divide_by_days_in_period=True,
            timestamp_column="StartedDateTime",
            period_days=1,
            stop_at_last_timestamp=True,
        )
    )


if __name__ == "__main__":
    test()
