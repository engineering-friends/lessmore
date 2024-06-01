import tempfile


def gen_temp_filename():
    return tempfile.NamedTemporaryFile(dir="/tmp", delete=False).name
