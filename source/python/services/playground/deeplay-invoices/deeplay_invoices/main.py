from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from deeplay_invoices.generate_act import generate_docx_and_pdf
from deeplay_invoices.generate_invoice import generate_invoice
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.system.open_in_os import open_in_os
from lessmore.utils.to_anything.to_datetime import to_datetime


def main(
    n: int,
    amount: int,
    amount_words: str,
    paid_month_at: datetime,
):
    # - Setup logger

    setup_json_loguru()

    # - Get replacements

    now = datetime.now()

    replacements = {
        # - Unchanged
        "SERVICE_AGREEMENT": "Service Agreement No1-09/24 from 02.09.2024",
        # - Auto
        "TODAY_MM_YY": now.strftime("%m/%y"),
        "TODAY_YYYY_MM_DD": now.strftime("%Y-%m-%d"),
        # - Changed
        "N": n,
        "HOURS": int(amount / 50),
        "INT_AMOUNT": amount,
        "AMOUNT_WORDS": amount_words,
        "PAID_MONTH_YYYY_MM": paid_month_at.strftime("%Y-%m"),
    }

    # - Generate act

    output_act_docx = f"data/{paid_month_at.strftime('%Y-%m')} act.docx"

    generate_docx_and_pdf(
        template_docx="generate_act_template.docx",
        replacements=replacements,
        output_docx=output_act_docx,
    )

    # - Generate invoice

    output_invoice_xlsx = f"data/{paid_month_at.strftime('%Y-%m')} invoice.xlsx"

    generate_invoice(
        template_xlsx="generate_invoice_template.xlsx",
        replacements=replacements,
        output_xlsx=output_invoice_xlsx,
    )

    # - Open files one by one

    open_in_os(output_act_docx.replace(".docx", ".pdf"))
    open_in_os(output_invoice_xlsx)


def test():
    main(
        n=20,
        amount=7500,
        amount_words="seven thousand five hundred",
        paid_month_at=to_datetime("2024.09.01"),
    )


if __name__ == "__main__":
    test()
