from functools import reduce
from typing import *

import pandas as pd

from family_fund.currencies.get_prices import get_prices
from family_fund.time import to_datetime
from loguru import logger


class Exchange:
    def __init__(
        self, base_asset, bank_asset="Банк", currencies=("USD", "EUR"), start_date="2018.01.01", is_test=False
    ):
        self.tdf = pd.DataFrame(columns=["date", "a", "b", "asset", "amount", "goal", "comment"])  # state core
        self.base_asset = base_asset
        self.bank_asset = bank_asset
        self.currencies = currencies
        self.start_date = start_date
        self.is_test = is_test

        self.current_date = to_datetime("2018.01.01")

    def calculate_balance(self, asset):
        df1 = self.tdf[self.tdf["b"] == asset].groupby("asset").amount.sum()
        df2 = self.tdf[self.tdf["a"] == asset].groupby("asset").amount.sum()
        return df1.subtract(df2, fill_value=0).to_dict()

    def cast_balance(self, balance_obj):
        "Canonical assets is a dictionary {asset: amount}"
        if isinstance(balance_obj, dict):
            return balance_obj
        elif isinstance(balance_obj, str):
            return self.calculate_balance(asset=balance_obj)
        elif isinstance(balance_obj, pd.Series):
            return balance_obj.to_dict()
        elif balance_obj is None:
            return {}
        else:
            raise Exception("Unknown assets type")

    # @property
    # def current_date(self):
    #     if len(self.tdf) == 0:
    #         return self.start_date
    #
    #     return self.tdf.iloc[-1]["date"]

    def get_price(self, asset, timestamp):
        if asset == self.base_asset:
            return 1.0

        return float(
            get_prices(str(to_datetime(timestamp))[:10], currencies=self.currencies, is_test=self.is_test).get(asset, 0)
        )

    def get_issued_amount(self, asset):
        return -self.calculate_balance(self.bank_asset).get(asset, 0)

    def convert_balance_to_base_assets(self, balance):
        balance = self.cast_balance(balance)

        if not balance:
            return balance

        values = []
        for asset, value in balance.items():
            s = self.calculate_balance(asset)
            if len(s) > 0:
                asset_issued_amount = self.get_issued_amount(asset)
                ratio = value / asset_issued_amount
                values.append(ratio * pd.Series(self.convert_balance_to_base_assets(s)))
            else:
                values.append(pd.Series([value], index=[asset]))

        return reduce(lambda a, b: a.add(b, fill_value=0), values).to_dict()

    def convert_balance_to_base_asset(self, balance):
        logger.debug("Converting balance to base asset", balance=balance)
        balance = self.cast_balance(balance)

        if not balance:
            return {self.base_asset: 0}

        balance = self.convert_balance_to_base_assets(balance)
        res = 0
        for asset, value in balance.items():
            res += value * self.get_price(asset, self.current_date)
        return {self.base_asset: res}

    def convert_pair(self, asset_ab: str, amount_ab: Optional[float], asset_ba: str, amount_ba: Optional[float]):
        """
        Return conversion amount pair
        USD, 1, RUB, None -> 1, 110.2
        USD, None, RUB, 110.2 -> 1, 110.2
        USD, 1, Rub, 110.2 -> 1, 110.2
        """
        assert amount_ab or amount_ba

        if not amount_ba:
            cap_ab = self.convert_balance_to_base_asset({asset_ab: amount_ab})[self.base_asset]
            price_ba = self.convert_balance_to_base_asset({asset_ba: 1})[self.base_asset]

            amount_ba = cap_ab / price_ba

        if not amount_ab:
            amount_ba, amount_ab = self.convert_pair(asset_ba, amount_ba, asset_ab, amount_ab)

        return amount_ab, amount_ba

    def submit_transactions(self, transactions):
        new_tdf = pd.DataFrame(transactions, columns=["date", "a", "b", "asset", "amount", "goal", "comment", "type"])
        new_tdf["amount"] = new_tdf["amount"].astype(float)
        self.tdf = pd.concat([self.tdf, new_tdf], axis=0)

    def gen_transactions(self, deal, deal_type):

        # - Set new current date

        assert deal["date"] >= self.current_date, "Reverse date order"
        self.current_date = deal["date"]

        res = []
        if deal_type == "simple":
            deal["type"] = "simple"
            res = [deal]
        elif deal_type == "exchange":
            res = []
            amount1, amount2 = self.convert_pair(deal["asset1"], deal["amount1"], deal["asset2"], deal["amount2"])
            side = str(deal["sides"])

            if not side or "1" in side:

                # make a -> b transaciton
                res.append(
                    dict(
                        type="exchange",
                        a=deal["a1"],
                        b=deal["b1"],
                        asset=deal["asset1"],
                        amount=amount1,
                        comment=deal["comment"],
                        date=deal["date"],
                        goal=deal["goal"],
                    )
                )

            if not side or "2" in side:

                # make b -> a transaciton
                res.append(
                    dict(
                        type="exchange",
                        a=deal["a2"],
                        b=deal["b2"],
                        asset=deal["asset2"],
                        amount=amount2,
                        comment=deal["comment"],
                        date=deal["date"],
                        goal=deal["goal"],
                    )
                )
        return res


if __name__ == "__main__":
    pass
