from pprint import pprint


values = """- Advertising
- Work""".split(
    "\n"
)

TOPICS = [value.replace("-", "").strip() for value in values if value]


def test():
    pprint(TOPICS)


if __name__ == "__main__":
    test()
