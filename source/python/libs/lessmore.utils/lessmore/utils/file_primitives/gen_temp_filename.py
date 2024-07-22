import tempfile


def gen_temp_filename(dir="/tmp", extension=""):
    return tempfile.NamedTemporaryFile(dir=dir.removesuffix("/"), delete=False).name + extension
