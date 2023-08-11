import re


def add_suffix_and_prefix_to_aliases(sql, prefix="", suffix=""):
    aliases = []
    aliases += re.findall(r"[aA][sS]\s+([a-zA-Z0-9_]+),", sql)  # 0.8 AS threshold,
    aliases += re.findall(r"([a-zA-Z0-9_]+) [aA][sS]\s\(", sql)  # threshold AS (

    for alias in aliases:
        # - Replace word aliases adding prefix and suffix

        sql = re.sub(rf"\b{alias}\b", f"{prefix}{alias}{suffix}", sql)

    return sql


def test():
    assert (
        add_suffix_and_prefix_to_aliases("0.8 AS threshold,", suffix="_suffix", prefix="prefix_")
        == "0.8 AS prefix_threshold_suffix,"
    )


if __name__ == "__main__":
    test()
