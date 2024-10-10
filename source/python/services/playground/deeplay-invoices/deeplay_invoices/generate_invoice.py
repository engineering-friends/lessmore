from datetime import datetime
from typing import TYPE_CHECKING

from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.system.open_in_os import open_in_os
from loguru import logger
from openpyxl import load_workbook

from deeplay.utils.tested import tested


if TYPE_CHECKING:
    from deeplay_invoices import main


@tested(tests=[main] if TYPE_CHECKING else [])
def generate_invoice(
    template_xlsx: str,
    replacements: dict,
    output_xlsx: str = "output.xlsx",
):
    # - Load the Excel template

    workbook = load_workbook(template_xlsx)
    sheet = workbook.active  # Assuming you're working with the first sheet

    # - Replace placeholders in the Excel sheet

    for row in sheet.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                try:
                    for key, value in replacements.items():
                        # - Get placeholder

                        placeholder = "{" + key + "}"

                        # - Check if placeholder is present

                        if placeholder not in str(cell.value):
                            continue

                        # - Replace placeholder with actual value

                        cell.value = cell.value.replace(placeholder, str(value))

                        # - Convert int placeholders

                        if key.startswith("INT_"):
                            cell.value = int(cell.value)

                    if "{" in str(cell.value) or "}" in str(cell.value):
                        raise Exception("Failed to replace all placeholders")
                except:
                    logger.exception("Failed to replace placeholders", text=cell.value)
                    raise

    # - Save the modified Excel document

    workbook.save(ensure_path(output_xlsx))
