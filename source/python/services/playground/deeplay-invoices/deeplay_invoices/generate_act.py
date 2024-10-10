from datetime import datetime

from docx import Document
from docx2pdf import convert
from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.system.open_in_os import open_in_os


def generate_act(
    template_filename: str = "generate_act_template.docx",
    replacements: dict = {},
    output_docx: str = "output.docx",
):
    # - Load the DOCX template

    doc = Document(template_filename)

    # - Replace placeholders with actual values

    # - Paragraphs

    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            print(run.text)
            run.text = run.text.format(**replacements)

    # - Tables

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.text = run.text.format(**replacements)

    # - Save the document

    doc.save(ensure_path(output_docx))

    # - Convert to pdf

    convert(output_docx, output_docx.replace(".docx", ".pdf"))


if __name__ == "__main__":
    output_path = "../data/2024-09 act.docx"
    now = datetime.now()

    generate_act(
        output_docx=output_path,
        replacements={
            # - Unchanged
            "FULL_NAME": "Arsenii Kadaner",
            "ID": "105550154",
            "AGREEMENT": "Service Agreement No1-09/24 from 02.09.2024",
            # - Auto
            "TODAY_MM": now.strftime("%m"),
            "TODAY_YY": now.strftime("%y"),
            "TODAY_YYYY-MM-DD": now.strftime("%Y-%m-%d"),
            # - Changed
            "N": 20,
            "HOURS": int(7500 / 50),
            "AMOUNT": 7500,
            "AMOUNT_WORDS": "seven hundred and fifty",
            "PAID_MONTH_YYYY-MM": "2024-09",
        },
    )
    open_in_os(output_path.replace(".docx", ".pdf"))
