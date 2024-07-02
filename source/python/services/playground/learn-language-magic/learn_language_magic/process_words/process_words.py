from learn_language_magic.process_words.extract_words import extract_words


def process_words(word_groups: dict):
    # - Extract words from stories

    word_groups = {k: v if isinstance(v, list) else extract_words(v) for k, v in word_groups.items()}

    # - Normalize words from groups


def test():
    print(
        process_words(
            word_groups={
                "story1": "Foo met a Bar",
                "group_1": ["Who", "Am", "I"],
            }
        )
    )


if __name__ == "__main__":
    test()
