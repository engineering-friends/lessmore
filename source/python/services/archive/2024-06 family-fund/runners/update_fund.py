from deeplay.utils.get_root_directory import get_root_directory
from deeplay.utils.loguru_utils import configure_loguru
from family_fund.update import update


configure_loguru()


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
)
