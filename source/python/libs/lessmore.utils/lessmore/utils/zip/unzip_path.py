import os
import zipfile

from lessmore.utils.zip import zip_path


def unzip_path(path, output_path="."):
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(output_path)


def test():

    # - Create sample file

    with open("test.txt", "w") as f:
        f.write("sample text")

    # - Zip file

    zip_path("test.txt", "test.zip")

    # - Remove original file

    os.remove("test.txt")

    # - Unzip file

    unzip_path("test.zip")

    # - Check if unzipped file exists

    assert os.path.exists("test.txt")

    # - Remove unzipped file

    os.remove("test.txt")
    os.remove("test.zip")


if __name__ == "__main__":
    test()
