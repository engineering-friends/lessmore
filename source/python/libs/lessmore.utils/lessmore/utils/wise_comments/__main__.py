import fire

from lessmore.utils.list_files import list_files
from lessmore.utils.loguru_utils import configure_loguru
from lessmore.utils.wise_comments.format_file import format_file


def main(*sources):
    assert len(sources) > 0, "Specify sources"
    for source in sources:
        for filename in list_files(source):
            format_file(filename)


if __name__ == "__main__":
    configure_loguru()
    fire.Fire(main)
