import pandas as pd

from clickhouse_sample.clickhouse_connection_string import clickhouse_connection_string
from sqlalchemy import create_engine


def test_connection():
    engine = create_engine(clickhouse_connection_string)
    table_df = pd.read_sql_query("SELECT 1", con=engine)

    print(table_df)


if __name__ == "__main__":
    test_connection()
