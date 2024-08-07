import asyncio

from dataclasses import dataclass

from better_notion_ai_autofill.autofill import autofill
from better_notion_ai_autofill.column.auto_column import auto_column
from learn_language_magic.ask import ask


@dataclass
class Vocabulary:
    name: str
    deck: str
    bundle: str

    @auto_column
    async def bundle_emoji(self):
        if not self.bundle:
            return ""
        return await ask(f"SINGLE emoji representing words {self.bundle}, only one", example="🔥")

    @auto_column
    async def emoji(self):
        return await ask(f"SINGLE emoji representing words {self.name}, only one", example="🔥")

    @auto_column
    async def translation(self):
        return await ask(f"English translation of german `{self.name}`", example="Run")

    @auto_column
    async def pronunciation(self):
        return str(await ask(f"Pronunciation of german `{self.name}`", example="/ɪç ˈtʁɪŋkə/"))

    @auto_column
    async def plural(self):
        is_noun = await ask(f"Is german `{self.name}` a noun?", example="yes") == "yes"
        if not is_noun:
            return ""
        else:
            return await ask(f"Plural of german `{self.name}`", example="Hunde")


if __name__ == "__main__":
    from learn_language_magic.deps import Deps

    asyncio.run(
        autofill(
            row_cls=Vocabulary,
            database_id="1f38a3aab8c14da19bb1b4317bdbc148",
            notion_token=Deps.load().config.notion_token,
        )
    )
