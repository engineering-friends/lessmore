import asyncio

from dataclasses import dataclass

from better_notion_ai_autofill.autofill import autofill
from better_notion_ai_autofill.column.auto_column import auto_column
from learn_language_magic.ask import ask


@dataclass
class Vocabulary:
    front: str
    deck: str
    bundle: str
    back: str

    @auto_column
    async def emoji(self):
        return await ask(f"SINGLE emoji representing words {self.front}, only one", example="🔥")

    @auto_column
    async def translation(self):
        return await ask(f"English translation of german `{self.front}`", example="Run")

    @auto_column
    async def pronunciation(self):
        return str(await ask(f"Pronunciation of german `{self.front}`", example="/ɪç ˈtʁɪŋkə/"))

    @auto_column
    async def plural(self):
        is_noun = await ask(f"Is german `{self.front}` a noun?", example="yes") == "yes"
        if not is_noun:
            return ""
        else:
            return await ask(f"Plural of german `{self.front}`", example="Hunde")

    @auto_column
    async def front_card(self):
        return f"{await self.emoji} {self.front or self.translation}"

    @auto_column
    async def back_card(self):
        return self.back if not self.plural else f"{self.back} ({await self.plural})"


if __name__ == "__main__":
    from learn_language_magic.deps import Deps

    asyncio.run(
        autofill(
            row_cls=Vocabulary,
            database_id="1f38a3aab8c14da19bb1b4317bdbc148",
            notion_token=Deps.load().config.notion_token,
        )
    )
