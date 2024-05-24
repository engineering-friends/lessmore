import json

from typing import Any


def _add_color_tags_to_json(record_dic: dict, record: Any = None):
    # - Get json

    output = json.dumps(record_dic, default=str, ensure_ascii=False).replace("{", "{{").replace("}", "}}")

    # - Iterate over json and add color tags

    for i, (key, value) in enumerate(record_dic.items()):
        # - Pick color

        color = {
            "ts": "green",
            "module": "cyan",
            "message": "level",
            "error": "red",
            "traceback": "red",
        }.get(key, "yellow")

        # - Dump to json

        value_str = json.dumps(value, default=str, ensure_ascii=False).replace("{", "{{").replace("}", "}}")

        # - Add colors for keys and values

        output = output.replace(
            f'"{key}": {value_str}',
            f'<{color}>"{{extra[_extra_{2 * i}]}}": {{extra[_extra_{2 * i + 1}]}}</{color}>',
        )

        # - Add key and value to record, from where loguru will get them

        # INPURE
        if record:
            record["extra"][f"_extra_{2 * i}"] = key
            record["extra"][f"_extra_{2 * i + 1}"] = json.dumps(value, default=str)

    return "<white>" + output + "\n" + "</white>"


def test():
    print(_add_color_tags_to_json({"foo": "bar"}))


if __name__ == "__main__":
    test()
