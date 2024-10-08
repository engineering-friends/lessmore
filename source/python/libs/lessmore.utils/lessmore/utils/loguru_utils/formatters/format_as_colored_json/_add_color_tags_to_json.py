import json

from typing import Any


def _add_color_tags_to_json(
    record_dic: dict,
    record: Any = None,  # will be modified!
    append_non_json_traceback: bool = True,
) -> str:
    # - Get json

    output = json.dumps(record_dic, default=str, ensure_ascii=False).replace("{", "{{").replace("}", "}}")

    # - Iterate over json and add color tags

    for i, (key, value) in enumerate(record_dic.items()):
        # - Pick color

        color_key = {
            "ts": "green",
            "module": "cyan",
            "msg": "level",
            "error": "red",
            "traceback": "red",
        }.get(key, "magenta")

        color_value = {
            "ts": "green",
            "module": "cyan",
            "msg": "level",
            "error": "red",
            "traceback": "red",
        }.get(key, "yellow")

        # - Dump to json

        value_str = json.dumps(value, default=str, ensure_ascii=False).replace("{", "{{").replace("}", "}}")

        # - Add colors for keys and values

        output = output.replace(
            f'"{key}": {value_str}',
            f'<{color_key}>"{{extra[_extra_{2 * i}]}}"</{color_key}>: <{color_value}>{{extra[_extra_{2 * i + 1}]}}</{color_value}>',
        )

        # - Add key and value to record, from where loguru will get them

        if record:
            record["extra"][f"_extra_{2 * i}"] = key
            record["extra"][f"_extra_{2 * i + 1}"] = json.dumps(value, ensure_ascii=False, default=str)

    # - Add traceback on new line

    if append_non_json_traceback and "traceback" in record_dic:
        record["extra"]["_extra_traceback"] = record_dic["traceback"]
        output += "\n<red>{extra[_extra_traceback]}</red>"

    # - Add white color for the whole output

    result = "<white>" + output + "\n" + "</white>"

    # - Return result

    return result


def test():
    print(_add_color_tags_to_json({"foo": "bar"}))


if __name__ == "__main__":
    test()
