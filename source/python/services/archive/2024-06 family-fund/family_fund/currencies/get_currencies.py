import functools
import os

from cache_to_disk import UNLIMITED_CACHE_AGE, NoCacheCondition, cache_to_disk
from pycbrf import Banks, ExchangeRates


# - set disk cache dir to current direcotry
os.environ["DISK_CACHE_DIR"] = os.path.join(os.getcwd(), ".cache/")


def _make_directories(path):
    if not path:
        return
    dirname = os.path.dirname(path)
    if not dirname:
        return
    if not os.path.exists(dirname):
        os.makedirs(dirname)


_make_directories(os.path.join(os.getcwd(), ".cache/"))


def get_all_currency_codes():
    content = httpx.get("http://download.geonames.org/export/dump/countryInfo.txt").text
    res = []

    lines = content.split("\n")

    for line in lines:
        if not line.startswith("#"):
            line = line.split("\t")
        try:
            if line[10]:
                res.append(line[10])
        except IndexError:
            pass
    return res[
        36::
    ]  # ['EUR', 'AED', 'AFN', 'XCD', 'XCD', 'ALL', 'AMD', 'AOA', 'ARS', 'USD', 'EUR', 'AUD', 'AWG', 'EUR', 'AZN', 'BAM', 'BBD', 'BDT', 'EUR', 'XOF', 'BGN', 'BHD', 'BIF', 'XOF', 'EUR', 'BMD', 'BND', 'BOB', 'USD', 'BRL', 'BSD', 'BTN', 'NOK', 'BWP', 'BYN', 'BZD', 'CAD', 'AUD', 'CDF', 'XAF', 'XAF', 'CHF', 'XOF', 'NZD', 'CLP', 'XAF', 'CNY', 'COP', 'CRC', 'CUP', 'CVE', 'ANG', 'AUD', 'EUR', 'CZK', 'EUR', 'DJF', 'DKK', 'XCD', 'DOP', 'DZD', 'USD', 'EUR', 'EGP', 'MAD', 'ERN', 'EUR', 'ETB', 'EUR', 'FJD', 'FKP', 'USD', 'DKK', 'EUR', 'XAF', 'GBP', 'XCD', 'GEL', 'EUR', 'GBP', 'GHS', 'GIP', 'DKK', 'GMD', 'GNF', 'EUR', 'XAF', 'EUR', 'GBP', 'GTQ', 'USD', 'XOF', 'GYD', 'HKD', 'AUD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'EUR', 'ILS', 'GBP', 'INR', 'USD', 'IQD', 'IRR', 'ISK', 'EUR', 'GBP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'AUD', 'KMF', 'XCD', 'KPW', 'KRW', 'EUR', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'XCD', 'CHF', 'LKR', 'LRD', 'LSL', 'EUR', 'EUR', 'EUR', 'LYD', 'MAD', 'EUR', 'MDL', 'EUR', 'EUR', 'MGA', 'USD', 'MKD', 'XOF', 'MMK', 'MNT', 'MOP', 'USD', 'EUR', 'MRU', 'XCD', 'EUR', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'XPF', 'XOF', 'AUD', 'NGN', 'NIO', 'EUR', 'NOK', 'NPR', 'AUD', 'NZD', 'NZD', 'OMR', 'PAB', 'PEN', 'XPF', 'PGK', 'PHP', 'PKR', 'PLN', 'EUR', 'NZD', 'USD', 'ILS', 'EUR', 'USD', 'PYG', 'QAR', 'EUR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SSP', 'SEK', 'SGD', 'SHP', 'EUR', 'NOK', 'EUR', 'SLL', 'EUR', 'XOF', 'SOS', 'SRD', 'STN', 'USD', 'ANG', 'SYP', 'SZL', 'USD', 'XAF', 'EUR', 'XOF', 'THB', 'TJS', 'NZD', 'USD', 'TMT', 'TND', 'TOP', 'TRY', 'TTD', 'AUD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'USD', 'UYU', 'UZS', 'EUR', 'XCD', 'VES', 'USD', 'USD', 'VND', 'VUV', 'XPF', 'WST', 'YER', 'EUR', 'ZAR', 'ZMW', 'ZWL', 'RSD', 'ANG']


@functools.lru_cache(365 * 10)
@cache_to_disk(UNLIMITED_CACHE_AGE)
def get_currencies(date, currency_codes):
    res = {}

    rates = ExchangeRates(date, locale_en=True)

    for currency_code in currency_codes:
        if rates[currency_code]:
            res[currency_code] = rates[currency_code].rate
    return res


if __name__ == "__main__":
    print(get_currencies("2020-01-01", ("USD", "EUR")))
