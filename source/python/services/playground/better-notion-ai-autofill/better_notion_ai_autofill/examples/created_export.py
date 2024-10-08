import asyncio

from dataclasses import dataclass
from datetime import datetime

from better_notion_ai_autofill.autofill import autofill
from better_notion_ai_autofill.column.auto_column import auto_column
from learn_language_magic.ask import ask


@dataclass
class CreatedExport:
    Created: datetime

    @auto_column(alias="Created Export")
    async def created_export(self):
        return self.Created


if __name__ == "__main__":
    from learn_language_magic.deps import Deps

    for database_id in [...]:
        asyncio.run(
            autofill(
                row_cls=CreatedExport,
                database_id=database_id,
                notion_token=Deps.load().config.notion_token,
            )
        )
