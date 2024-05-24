import os


SUPPORTED_EXTENSIONS = [".json", ".yaml"]


def read_config_file(filename: str) -> dict:
    # - Get extension

    extension = os.path.splitext(filename)[-1]

    assert extension in SUPPORTED_EXTENSIONS, f"Non supported config extension: {extension}"

    # - Get content

    content = read_file(filename)

    # - Decode

    if extension == ".json":
        return decode_from_json(content)
    elif extension == ".yaml":
        return decode_from_yaml(content)


def test():
    # - Write sample file

    write_file(content='{"a": 1}', path="/tmp/sample.json")

    # - Read sample file

    assert read_config_file("/tmp/sample.json") == {"a": 1}

    # - Write sample file

    write_file(content="a: 1", path="/tmp/sample.yaml")

    # - Read sample file

    assert read_config_file("/tmp/sample.yaml") == {"a": 1}

    # - Delete sample files

    os.remove("/tmp/sample.json")
    os.remove("/tmp/sample.yaml")


if __name__ == "__main__":
    test()
