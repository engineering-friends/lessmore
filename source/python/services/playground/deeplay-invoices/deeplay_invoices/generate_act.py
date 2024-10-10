import os.path

from datetime import datetime
from typing import TYPE_CHECKING

from docx import Document
from docx2pdf import convert
from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.system.open_in_os import open_in_os
from loguru import logger
from markdown_it.rules_block import paragraph

from deeplay.utils.tested import tested


if TYPE_CHECKING:
    from deeplay_invoices import main


@tested(tests=[main] if TYPE_CHECKING else [])
def generate_docx_and_pdf(
    template_docx: str,
    replacements: dict,
    output_docx: str = "output.docx",
):
    # - Load the DOCX template

    doc = Document(template_docx)

    # - Replace placeholders with actual values

    # -- Collect runs from paragraphs and tables

    runs = []

    runs += sum([paragraph.runs for paragraph in doc.paragraphs], [])
    runs += sum(
        [
            paragraph.runs
            for table in doc.tables
            for row in table.rows
            for cell in row.cells
            for paragraph in cell.paragraphs
        ],
        [],
    )

    # -- Fix placeholders

    for run in runs:
        try:
            run.text = run.text.format(**replacements)
        except:
            logger.exception("Failed to replace placeholders", text=run.text)
            raise

    # - Save the document

    doc.save(ensure_path(output_docx))

    # - Convert to pdf

    convert(output_docx, output_docx.replace(".docx", ".pdf"))
