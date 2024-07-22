import asyncio

from dataclasses import dataclass

from learn_language_magic.ask import ask
from notion_database_ai.field.auto_column import auto_column
from notion_database_ai.update_notion_database import update_notion_database


@dataclass
class Vocabulary:
    name: str
    group: list[str]
    bundle: str

    @auto_column
    async def emoji(self):
        return await ask(f"Single emoji representing {self.bundle}")


if __name__ == "__main__":
    from learn_language_magic.deps import Deps

    asyncio.run(
        update_notion_database(
            row_class=Vocabulary,
            database_id="1f38a3aab8c14da19bb1b4317bdbc148",
            notion_token=Deps.load().config.notion_token,
        )
    )
