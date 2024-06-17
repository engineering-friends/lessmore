import decimal

from dateutil.parser import parse as parse_date
from family_fund.currencies.get_currencies import get_currencies
from family_fund.currencies.get_real_estate_estimator import get_real_estate_estimator


CURRENCY_CODES = ("USD", "EUR")

REAL_ESTATE = {
    "Квартира на Народном Ополчении": {"dt": "2021.11.05", "value": 15_000_000},
    "Квартира в Медведково": {"dt": "2021.11.05", "value": 9_000_000},
    "Никольский Дом": {"dt": "2021.11.05", "value": 7_000_000},
    "Матвейцевский Дом": {"dt": "2021.11.05", "value": 6_000_000},
    "Квартира на Теплом Стане": {"dt": "2021.11.05", "value": 9_200_000},
    "Квартира на Славянском Бульваре": {"dt": "2021.11.05", "value": 8_600_000},
}


def get_prices(dt, currencies=CURRENCY_CODES, is_test=False):
    dt = parse_date(dt)

    if is_test:
        return {"USD": 100 * max(1, dt.year - 2021), "EUR": 100 * max(1, dt.year - 2021)}

    res = {}

    # - Add currencies

    res.update(get_currencies(dt, currencies))

    # - Add real estate

    estimator = get_real_estate_estimator()
    for k, v in REAL_ESTATE.items():
        res[k] = decimal.Decimal(round(estimator(dt, v)))

    return res


if __name__ == "__main__":
    print(get_prices("2022.08.01"))
