import os

import notifiers

from family_fund.numeric import *


def round_dataframe(df, a=0.001):
    return df.applymap(lambda v: v if is_none(v) else custom_round(v, a))


def remove_empty_lines(df):
    return df[df.fillna(0).astype(float).sum(axis=1).abs() > 1e-5]


def send_to_telegram(chat_id, msg, token):
    telegram = notifiers.get_notifier("telegram")
    telegram.notify(message=msg, token=token, chat_id=chat_id, parse_mode="html")


if __name__ == "__main__":
    import os

    os.environ["TELEGRAM_BOT_TOKEN"] = "..."
    send_to_telegram(
        "160773045",
        """*Отчет о состоянии семейного фонда от 2022.01.01*

Общий баланс: 
- Валюта: 5,642,000.0
- Недвижимость: 44,644,000.0
- Всего: 50,286,000.0

В плюсе: 
+ Мама: 505,000 руб.

В минусе: 
+ Марк: -228,000 руб.
+ Саша: -252,000 руб.
+ Тима: -668,000 руб.
+ Дато: -904,000 руб.
+ Сима: -940,000 руб. 

Для более детального анализа, можно изучить таблицу по ссылке: https://docs.google.com/spreadsheets/d/1fNSAg6nBx7DJ8ifJ1LcW3JWzcuDN4_PAMOc13lm_4y0/edit?usp=sharing

""",
    )
