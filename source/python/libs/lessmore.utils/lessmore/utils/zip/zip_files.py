import os
import zipfile

from pathlib import Path


def zip_files(filenames: list[str], output_filename: str) -> None:
    with zipfile.ZipFile(output_filename, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in filenames:
            archive.write(filename, arcname=os.path.basename(filename))
    return output_filename


def test():
    zip_files(
        [str(Path(__file__).parent / "zip_path.py"), str(Path(__file__).parent / "zip_files.py")],
        output_filename="test.zip",
    )
    assert os.path.exists("test.zip")
    os.remove("test.zip")


if __name__ == "__main__":
    test()
