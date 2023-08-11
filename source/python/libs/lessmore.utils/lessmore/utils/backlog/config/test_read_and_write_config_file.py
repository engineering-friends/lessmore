from lessmore.utils.config.read_config_file import read_config_file
from lessmore.utils.config.write_config_file import write_config_file


def test_read_and_write_config_file():
    from lessmore.utils.coder.sample_data import sample_data

    for filename in ["/tmp/sample.json", "/tmp/sample.yaml"]:
        write_config_file(sample_data, filename, is_stringified=False)

        assert read_config_file(filename) == sample_data

    for filename in ["/tmp/sample.json", "/tmp/sample.yaml", "/tmp/sample.env"]:
        write_config_file(sample_data, filename, is_stringified=True)

        print("Stringified config", read_config_file(filename))


if __name__ == "__main__":
    test_read_and_write_config_file()
