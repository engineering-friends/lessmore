import os
import zipfile

from lessmore.utils.path_helpers.get_current_dir import get_current_dir


def zip_files(filenames, output_filename):
    with zipfile.ZipFile(output_filename, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in filenames:
            archive.write(filename, arcname=os.path.basename(filename))


def test():
    zip_files(
        [str(get_current_dir() / "zip_path.py"), str(get_current_dir() / "zip_files.py")], output_filename="test.zip"
    )
    assert os.path.exists("test.zip")
    os.remove("test.zip")


if __name__ == "__main__":
    test()
