import typer

from lessmore.utils.file_primitives.list_files import list_files
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.wise_comments.format_file import format_file


def main(sources: list[str]):
    assert len(sources) > 0, "Specify sources"
    for source in sources:
        for filename in list_files(source):
            format_file(filename)


if __name__ == "__main__":
    setup_json_loguru()
    typer.run(main)
