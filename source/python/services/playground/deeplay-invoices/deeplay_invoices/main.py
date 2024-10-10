from datetime import datetime

from deeplay_invoices.generate_act import generate_act
from deeplay_invoices.generate_invoice import generate_invoice
from lessmore.utils.system.open_in_os import open_in_os


if __name__ == "__main__":
    # - Get replacements

    now = datetime.now()
    replacements = {
        # - Unchanged
        "SERVICE_AGREEMENT": "Service Agreement No1-09/24 from 02.09.2024",
        # - Auto
        "TODAY_MM": now.strftime("%m"),
        "TODAY_MM/YY": now.strftime("%m/%y"),
        "TODAY_YYYY-MM-DD": now.strftime("%Y-%m-%d"),
        # - Changed
        "N": 20,
        "HOURS": int(7500 / 50),
        "AMOUNT": 7500,
        "AMOUNT_WORDS": "seven hundred and fifty",
        "PAID_MONTH_YYYY-MM": "2024-09",
    }

    # - Generate act

    output_act_docx = f"../data/{now.strftime('%Y-%m')} act.docx"

    generate_act(
        output_docx=output_act_docx,
        replacements=replacements,
    )

    # - Generate invoice

    output_invoice_xlsx = f"../data/{now.strftime('%Y-%m')} invoice.xlsx"
    generate_invoice(
        template_filename="generate_invoice_template.xlsx",
        replacements=replacements,
        output_xlsx=output_invoice_xlsx,
    )

    # - Open files one by one

    open_in_os(output_act_docx.replace(".docx", ".pdf"))
    # open_in_os(output_invoice_xlsx)
