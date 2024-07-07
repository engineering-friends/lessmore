def test_parse_markdown_table():
    from lessmore.utils.enriched_notion_client.enriched_notion_client import EnrichedNotionAsyncClient

    print(
        EnrichedNotionAsyncClient.parse_markdown_table(
            """| Subject Pronoun | Conjugation |
| --- | --- |
| ich (I) | foo |
| du (you, singular informal) | bar |""",
            annotations=lambda header, row: {"bold": "foo" in row["Conjugation"]},
        )
    )


if __name__ == "__main__":
    test_parse_markdown_table()
