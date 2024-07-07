import pandas as pd


def markdown_table_to_df(markdown_table):
    # Split the markdown table into lines
    lines = markdown_table.strip().split("\n")

    # The first line is the header
    headers = [header.strip() for header in lines[0].split("|") if header.strip()]

    # The remaining lines are the data rows
    data = []
    for line in lines[2:]:
        row = [cell.strip() for cell in line.split("|") if cell.strip()]
        data.append(row)

    # Create a pandas DataFrame
    df = pd.DataFrame(data, columns=headers)
    return df


def test():
    markdown_table = """
    | Name    | Age | City       |
    |---------|-----|------------|
    | Alice   | 30  | New York   |
    | Bob     | 25  | Los Angeles|
    | Charlie | 35  | Chicago    |
    """

    df = markdown_table_to_df(markdown_table)
    print(df)


if __name__ == "__main__":
    test()
