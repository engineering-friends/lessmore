def test_parse_markdown_table():
    from lessmore.utils.enriched_notion_client.enriched_notion_client import EnrichedNotionAsyncClient

    assert EnrichedNotionAsyncClient.parse_markdown_table("""| Subject Pronoun | Conjugation |
| --- | --- |
| ich (I) |  |
| du (you, singular informal) |  |""") == {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": 2,
            "has_column_header": True,
            "has_row_header": False,
            "children": [
                {
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "Subject Pronoun"}}],
                            [{"type": "text", "text": {"content": "Conjugation"}}],
                        ]
                    },
                },
                {
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "ich (I)"}}],
                            [{"type": "text", "text": {"content": ""}}],
                        ]
                    },
                },
                {
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "du (you, singular informal)"}}],
                            [{"type": "text", "text": {"content": ""}}],
                        ]
                    },
                },
            ],
        },
    }


if __name__ == "__main__":
    test_parse_markdown_table()
