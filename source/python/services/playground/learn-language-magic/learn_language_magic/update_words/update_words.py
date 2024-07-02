from learn_language_magic.update_words.extract_words import extract_words


def update_words(word_groups: dict, notion_page_id: str):
    # - Extract words from stories

    word_groups = {k: v if isinstance(v, list) else extract_words(v) for k, v in word_groups.items()}

    # -


def test():
    print(
        update_words(
            word_groups={
                # "story1": "Foo met a Bar",
                "group_1": ["Who", "Am", "I"],
            }
        )
    )


if __name__ == "__main__":
    test()
