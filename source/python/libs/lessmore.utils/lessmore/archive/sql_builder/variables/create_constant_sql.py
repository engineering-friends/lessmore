from datetime import datetime

from lessmore.utils.unified import to_datetime_str


def create_constant_sql(value):
    if isinstance(value, str):
        return f"""'{value}'"""
    elif isinstance(value, datetime):
        return f"""toDateTime('{to_datetime_str(value, pattern="%Y-%m-%d %H:%M:%S")}')"""
    elif isinstance(value, bool):
        return str(value).upper()  # "TRUE" or "FALSE"
    else:
        return str(value)


def test():
    print(create_constant_sql(0.8))
    print(create_constant_sql(datetime.now()))
    print(create_constant_sql("Foo"))
    print(create_constant_sql(True))


if __name__ == "__main__":
    test()
