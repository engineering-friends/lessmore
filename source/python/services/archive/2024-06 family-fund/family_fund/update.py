import os.path
import sys

from datetime import datetime, timedelta

from lessmore.utils.read_config.read_config import read_config

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # todo maybe: make properly, hardcode [@marklidenberg]

import copy

import pandas as pd

from family_fund.exchange import Exchange
from family_fund.google_spreadsheet import SpreadSheetSyncer
from family_fund.utils import *
from loguru import logger


def update(spreadsheet_id: str, telegram_bot_token: str,base_asset: str = "RUB", hidden_rows: list[str] = [], is_test: bool = False,):
    # - Init google spreadsheet

    gs = SpreadSheetSyncer(spreadsheet_id)

    # - Init exchange

    exchange = Exchange(base_asset, is_test=is_test)

    # - Get transactions and exchanges

    # -- Load simple transactions

    df1 = gs.read("[Прямые транзакции]")
    df1 = df1.rename(
        columns={
            "Дата": "date",
            "А": "a",
            "Б": "b",
            "Актив": "asset",
            "Количество": "amount",
            "Цель": "goal",
            "Comment": "comment",
            "Неактивен": "is_inactive",
        }
    )
    df1 = df1[df1["is_inactive"].astype(str) != "1"]

    # -- Load exchanges

    df2 = gs.read("[Обмены]")
    df2 = df2.rename(
        columns={
            "Дата": "date",
            "А1": "a1",
            "Б1": "b1",
            "Актив1": "asset1",
            "Количество1": "amount1",
            "А2": "a2",
            "Б2": "b2",
            "Актив2": "asset2",
            "Количество2": "amount2",
            "Цель": "goal",
            "Комментарий": "comment",
            "Теги": "tags",
            "[Сторона]": "sides",
            "Неактивен": "is_inactive",
        }
    )

    # replace auto with None
    df2["amount1"] = np.where(df2["amount1"] == "auto", None, df2["amount1"])
    df2["amount2"] = np.where(df2["amount2"] == "auto", None, df2["amount2"])

    # convert to float and replace np.nan to None
    df2["amount1"] = df2["amount1"].astype(float).astype(object).replace(np.nan, None)
    df2["amount2"] = df2["amount2"].astype(float).astype(object).replace(np.nan, None)
    df2 = df2[df2["is_inactive"].astype(str) != "1"]

    # -- Load accounts

    df3 = gs.read("[Счета]")
    df3 = df3.rename(
        columns={
            "Статус": "status",
            "Название": "name",
            "Владелец": "owner",
            "Техническое название": "technical_name",
            "Тип": "type",
            "Описание": "description",
            "Дата создания счета": "opened_at",
            "Дата закрытия счета": "closed_at",
            "Комментарий": "comment",
        }
    )

    df3["date"] = df3["opened_at"]
    df3["a"] = "Банк"
    df3["b"] = df3["owner"]
    df3["asset"] = df3["name"]
    df3["amount"] = 1
    df3["goal"] = "Открытие счета"
    df3["comment"] = ""

    df3 = df3[["date", "a", "b", "asset", "amount", "goal", "comment"]]

    # -- Convert to transactions

    values = []
    for record in df1.to_dict(orient="records"):
        record["type"] = "simple"
        values.append(record)
    for record in df2.to_dict(orient="records"):
        record["type"] = "exchange"
        values.append(record)
    for record in df3.to_dict(orient="records"):
        record["type"] = "simple"
        values.append(record)

    type_order = {"simple": 1, "exchange": 2}
    values = list(sorted(values, key=lambda record: [record["date"], type_order[record["type"]]]))

    # - Submit all transactions

    for value in copy.deepcopy(values):
        logger.info("Processing", value=value)
        transactions = exchange.gen_transactions(value, value.pop("type"))
        exchange.submit_transactions(transactions)

    # - Add evaluation in rubles

    exchange.tdf["amount_in_base"] = exchange.tdf.apply(
        lambda row: row["amount"] * exchange.get_price(asset=row["asset"], timestamp=row["date"]), axis=1
    )

    # - Set yesterday as exchange current date

    exchange.current_date = datetime.now() - timedelta(days=1)

    # - Collect stats

    df = exchange.tdf
    logger.info(f"Got {len(df)} transactions")
    ASSETS = set(df["a"].unique()) | set(df["b"].unique())
    ASSETS = [a for a in ASSETS if isinstance(a, str) and a != "Банк"]
    ASSETS = list(sorted(ASSETS))

    # -- Assets

    values = []
    for asset in ASSETS:
        values.append(exchange.calculate_balance(asset))
    df = pd.DataFrame(values, index=ASSETS)
    df = round_dataframe(df)
    df = remove_empty_lines(df)
    _hidden_rows = [column for column in df.index if column in hidden_rows]
    df = df.drop(_hidden_rows)
    df = df.fillna(0)

    assets_df = df

    # -- Assets reduced to base assets

    values = []
    for asset in ASSETS:
        values.append(exchange.convert_balance_to_base_assets(asset))
    df = pd.DataFrame(values, index=ASSETS)
    df = round_dataframe(df)
    df = remove_empty_lines(df)
    _hidden_rows = [column for column in df.index if column in hidden_rows]

    df = df.drop(_hidden_rows)
    df = df.fillna(0)

    reduced_assets_df = df

    # -- Assets in base asset

    values = []
    for asset in ASSETS:
        values.append(exchange.convert_balance_to_base_assets(asset))
    df = pd.DataFrame(values, index=ASSETS)
    df = round_dataframe(df)
    df = remove_empty_lines(df)
    _hidden_rows = [column for column in df.index if column in hidden_rows]

    df = df.drop(_hidden_rows)
    df = df.fillna(0)
    df.index.name = None
    for column in df.columns:
        df[column] = df[column] * exchange.convert_balance_to_base_asset({column: 1})[base_asset]
    df = round_dataframe(df, 1 if is_test else 1000)

    # --- Extra groupings

    base_asset_columns = ["EUR", "USD", "RUB"]
    df["[Сумма базовых валют]"] = 0
    for asset in base_asset_columns:
        if asset in df.columns:
            df["[Сумма базовых валют]"] += df[asset].fillna(0)

    df["[Сумма недвижимости]"] = 0
    for col in df.columns:
        if "Квартира" in col or "Дом" in col:
            df["[Сумма недвижимости]"] += df[col].fillna(0)

    df["[Сумма]"] = df["[Сумма базовых валют]"] + df["[Сумма недвижимости]"]

    df = df[["[Сумма]", "[Сумма базовых валют]", "[Сумма недвижимости]"] + list(df.columns[:-3])]
    reduced_assets_in_base_asset_df = df

    # - Upload

    tdf = exchange.tdf[["date", "a", "b", "asset", "amount", "amount_in_base", "goal", "comment", "type"]]
    gs.write("Транзакции", tdf)
    gs.write("По активам", assets_df.reset_index())
    gs.write("По базовым активам", reduced_assets_df.reset_index())
    gs.write("В расчете на рубли", reduced_assets_in_base_asset_df.reset_index())

    if is_test:
        return

    # - Send telegram report

    def format_number(number):
        number = custom_round(int(number), 1000)
        return f"{int(number):,}"

    # -- Prepare data

    total_cash = df.loc["Фонд: бутово"]["[Сумма]"]
    total_real_estate = df.loc["Фонд: недвижимость"]["[Сумма]"]

    # total took rubles
    names = ["Мама", "Тима", "Сима", "Дато", "Саша", "Марк"]
    spending_rub = {}
    total_money_rub = {}

    for name in names:
        if name + ": личный" in df.index:
            spending_rub[name] = df.loc[name + ": личный"]["[Сумма]"]
        else:
            spending_rub[name] = 0
        if name + ": фонд" in df.index:
            total_money_rub[name] = df.loc[name + ": фонд"]["[Сумма]"]
        else:
            total_money_rub[name] = 0

    # Deprecated (2023.01.08)
    # def format_spending(amount):
    #     if amount < 0:
    #         return f"(вложил(а) в фонд {format_number(abs(amount))}р)"
    #     elif amount == 0:
    #         return ""
    #     elif amount > 0:
    #         return f"(взял(а) из фонда {format_number(abs(amount))}р)"

    # -- Format text

    text = """*Отчет о состоянии семейного фонда от {today}*

Общий баланс в расчете на рубли: 
- Валюта: {total_cash}р

Распределение в расчете на рубли:
{by_people}

Дата расчета: {current_date}.
Курсы на дату расчета: {rates}.

Более подробную информацию можно посмотреть по ссылке: https://docs.google.com/spreadsheets/d/1fNSAg6nBx7DJ8ifJ1LcW3JWzcuDN4_PAMOc13lm_4y0/edit?usp=sharing

    """.format(
        today=datetime.now().date(),
        total_cash=format_number(total_cash),
        total_real_estate=format_number(total_real_estate),
        total=format_number(total_cash + total_real_estate),
        current_date=exchange.current_date.date(),
        rates=", ".join(
            [f"{asset}={exchange.get_price(asset, exchange.current_date)}" for asset in exchange.currencies]
        ),
        by_people="\n".join(
            [
                # f"- {name}: {format_number(total_money_rub[name])}р {format_spending(spending_rub[name])}" # Deprecated (2023.01.08)
                f"- {name}: {format_number(total_money_rub[name])}р"
                for name in names
            ]
        ),
    )

    # -- Send text

    send_to_telegram(
        chat_id=160773045, # @marklidenberg
        msg=text,
        token=telegram_bot_token,
    )


def test():
    from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru


    setup_json_loguru()

    update(
        base_asset="RUB",
        # spreadsheet_id="1MRTy-cIk2lhinCDkVskUKF17xLyiLoonWLAnl17xV7g",  # Fund Test    # pragma: allowlist secret
        spreadsheet_id="1fNSAg6nBx7DJ8ifJ1LcW3JWzcuDN4_PAMOc13lm_4y0",  # Fund     # pragma: allowlist secret
        # spreadsheet_id="1WldwizrobgrnO1FYTGqr89x1Vb7sRatvowb_Ixyxftk",  # Fund till 2022.12.17     # pragma: allowlist secret
        hidden_rows=[
            # "Мама: личный",
            # "Тима: личный",
            # "Сима: личный",
            # "Дато: личный",
            # "Саша: личный",
            # "Марк: личный",
            "Папа: личный",
            # "Фонд: бутово",
            # "Фонд: недвижимость",
            "Папа",
            "Третья сторона",
        ],
        is_test=False,
        telegram_bot_token=read_config(source='config.yaml')['telegram_bot_token']
    )


if __name__ == '__main__':
    test()