import os
import zipfile


def zip_path(path, output_filename=None):
    """Creates a zip archive from the given path (file or folder)."""

    # If no output filename is given, use the base name of the input path
    if not output_filename:
        output_filename = os.path.basename(path) + ".zip"

    with zipfile.ZipFile(output_filename, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        if os.path.isfile(path):
            archive.write(path, arcname=os.path.basename(path))
        elif os.path.isdir(path):
            for foldername, subfolders, filenames in os.walk(path):
                for filename in filenames:

                    # - Create complete filepath of file in directory

                    file_path = os.path.join(foldername, filename)

                    # - Add file to zip archive with its relative path

                    archive.write(file_path, arcname=os.path.relpath(file_path, path))


def test():
    zip_path("unzip_file.py")
    assert os.path.exists("unzip_file.py.zip")
    os.remove("unzip_file.py.zip")


if __name__ == "__main__":
    test()
