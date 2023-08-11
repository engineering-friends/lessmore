from typing import Callable, Optional

import humanize
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def save_image_from_dataframe(
    df: pd.DataFrame,
    header_column_count: Optional[int] = None,
    header_row_count: Optional[int] = None,
    title: str = "Title",
    function_add_custom_style: Optional[Callable] = None,
    function_add_custom_style_kwargs: Optional[dict] = None,
    path: str = "image.png",
    col_width: float = 2.3,
    row_height: float = 0.8,
    font_size: int = 14,
    header_color: str = "#520091",
    row_colors: list = ["#8bd6cd", "#e9e4f7"],
    edge_color: str = "black",
    title_color="purple",
    bbox: list = [0, 0, 1, 1],
    **kwargs,
):
    """

    Parameters
    ----------
    df:
        Input DataFrame
    header_column_count:
        Number of header columns, starting at one
    header_row_count:
        Number of header rows, starting at one
    title:
        Text title over table
    function_add_custom_style:
        Custom function for add more feature to picture.
        Required add args: (value, cell, row_number, col_number, **kwargs).
        For example see tests in this file.
    function_add_custom_style_kwargs:
        Additional kwargs for 'function_add_custom_style'
    path:
        path to save picture
    col_width:

    row_height:

    font_size:

    header_color:

    row_colors:
        Two colors for even and odd numbers
    edge_color:
        border colour
    title_color:

    bbox:
        [x, y, height, width]
    kwargs
        Additional args for pyplot.table (https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.table.html)
    """
    size = (np.array(df.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
    fig, ax = plt.subplots(figsize=size)
    ax.axis("off")

    if header_row_count is not None:
        header_row_count -= 1  # because starts with 0
        mpl_table = ax.table(cellText=df.values, bbox=bbox, colLabels=df.columns, cellLoc="center", **kwargs)
    else:
        mpl_table = ax.table(cellText=df.values, bbox=bbox, cellLoc="center", **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for row_number, col_number, cell in [(row, column, cell) for (row, column), cell in mpl_table._cells.items()]:
        if header_row_count is not None:
            row_number = row_number - 1

        cell.set_edgecolor(edge_color)

        if (header_row_count is not None and row_number < header_row_count) or (
            header_column_count is not None and col_number < header_column_count
        ):
            cell.set_text_props(weight="bold", color="w")
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[row_number % len(row_colors) == 0])

        if function_add_custom_style is not None:

            if (row_number >= 0 and header_column_count is not None and col_number >= header_column_count) or (
                row_number >= 0 and header_column_count is None and col_number >= 0
            ):
                value = str(df.iloc[row_number, col_number]).replace(",", "")  # convert humanize view to int
                is_int = (value.startswith("-") and value[1:].isdigit()) or value.isdigit()
                is_float = isinstance(value, str) and value.replace(".", "").isdigit()
                if is_int or is_float:
                    value = int(value) if is_int else float(value)
                    function_add_custom_style(
                        value=value,
                        cell=cell,
                        row_number=row_number,
                        col_number=col_number,
                        df=df,
                        col_width=col_width,
                        row_height=row_height,
                        font_size=font_size,
                        header_color=header_color,
                        row_colors=row_colors,
                        edge_color=edge_color,
                        bbox=bbox,
                        header_column_count=header_column_count,
                        header_row_count=header_row_count,
                        ax=ax,
                        filename=path,
                        title=title,
                        **function_add_custom_style_kwargs if function_add_custom_style_kwargs else {},
                    )

    ax.set_title(title, color=title_color)

    fig = ax.get_figure()
    fig.savefig(path)


def test1():
    def _test_function_add_custom_style_1(value, cell, row_number, col_number, **kwargs):
        title = kwargs.get("title")
        header_row_count = kwargs.get("header_row_count")
        check_columns_ids = [4]  # MissedHands = 4
        check_zero_columns_ids = [1, 2]  # CSHands = 1, Hands=2
        red_color = "#bf0606"

        if row_number < header_row_count:
            return

        if col_number in check_columns_ids:
            if (value <= -1500 or value >= 5000) or (
                title != "PPPoker" and row_number >= 1 and value != 0
            ):  # table date in PPPoker table, so it can change within 3+- days
                cell.set_facecolor(red_color)
        if col_number in check_zero_columns_ids:
            if value == 0:
                cell.set_facecolor(red_color)

    # fmt: off
    df_test1 = pd.read_json(
        '{"HandDate":{"0":"2022-12-13","1":"2022-12-12","2":"2022-12-11","3":"2022-12-10","4":"2022-12-09","5":"2022-12-08","6":"2022-12-07","7":"2022-12-06","8":"2022-12-05","9":"2022-12-04","10":"2022-12-03"},"CSHands":{"0":"0","1":"1,294,707","2":"1,430,185","3":"1,487,718","4":"1,554,291","5":"1,528,263","6":"1,522,624","7":"1,515,693","8":"1,435,190","9":"1,394,774","10":"1,394,754"},"Hands":{"0":"0","1":"1,289,109","2":"1,425,935","3":"1,483,387","4":"1,549,834","5":"1,523,722","6":"1,518,165","7":"1,511,234","8":"1,430,880","9":"1,390,915","10":"1,390,957"},"Corrupt":{"0":"0","1":"5,755","2":"4,250","3":"4,331","4":"4,457","5":"4,541","6":"4,459","7":"4,459","8":"4,310","9":"3,859","10":"3,812"},"MissedHands":{"0":"0","1":"-157","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"30,000","9":"20,000","10":"10,000"}}')
    # fmt: on
    df_test1 = df_test1.applymap(lambda value: humanize.intcomma(value))
    df_test1.loc[:, "CSHands":] = df_test1.loc[:, "CSHands":].applymap(lambda value: humanize.intcomma(value))

    save_image_from_dataframe(
        df=df_test1,
        header_column_count=1,
        header_row_count=1,
        col_width=2.3,
        row_height=0.8,
        path="test1.png",
        title="Test1",  # 'This is title',
        function_add_custom_style=_test_function_add_custom_style_1,
    )


def test2():
    def _test_function_add_custom_style_2(value, cell, row_number, col_number, **kwargs):
        title = kwargs.get("title")
        check_columns_ids = [3]
        check_zero_columns_ids = [0, 1]

        if col_number in check_columns_ids:
            if (value <= -1500 or value >= 5000) or (
                title != "PPPoker" and row_number >= 1 and value != 0
            ):  # table date in PPPoker table, so it can change within 3+- days
                cell.set_facecolor("#bf0606")
        if col_number in check_zero_columns_ids:
            if value == 0:
                cell.set_facecolor("#bf0606")

    # fmt: off
    df_test2 = pd.read_json(
        '{"CSHands":{"0":"0","1":"1,294,707","2":"1,430,185","3":"1,487,718","4":"1,554,291","5":"1,528,263","6":"1,522,624","7":"1,515,693","8":"1,435,190","9":"1,394,774","10":"1,394,754"}," Hands":{"0":"0","1":"1,289,109","2":"1,425,935","3":"1,483,387","4":"1,549,834","5":"1,523,722","6":"1,518,165","7":"1,511,234","8":"1,430,880","9":"1,390,915","10":"1,390,957"}," Corrupt":{"0":"0","1":"5,755","2":"4,250","3":"4,331","4":"4,457","5":"4,541","6":"4,459","7":"4,459","8":"4,310","9":"3,859","10":"3,812"}," MissedHands":{"0":"0","1":"-157,000","2":"0","3":"0","4":"0","5":"0","6":"0","7":"0","8":"30,000","9":"20,000","10":"10,000"}}')
    # fmt: on

    df_test2 = df_test2.applymap(lambda value: humanize.intcomma(value))
    df_test2.loc[:, "CSHands":] = df_test2.loc[:, "CSHands":].applymap(lambda value: humanize.intcomma(value))
    save_image_from_dataframe(
        df=df_test2,
        col_width=2.0,
        path="test2.png",
        title="Test2",  # 'This is title',
        function_add_custom_style=_test_function_add_custom_style_2,
    )


if __name__ == "__main__":
    test1()
    test2()
