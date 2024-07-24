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
    async def emoji(self) -> str:
        return await ask(f"SINGLE emoji representing words {self.back}, only one", example="🔥")

    @auto_column
    async def translation(self) -> str:
        return await ask(f"English translation of german `{self.back}`", example="Run")

    @auto_column
    async def pronunciation(self) -> str:
        return str(await ask(f"Pronunciation of german `{self.back}`", example="/ɪç ˈtʁɪŋkə/"))

    @auto_column
    async def plural(self) -> str:
        is_noun = await ask(f"Is german `{self.back}` a noun?", example="yes") == "yes"
        if not is_noun:
            return ""
        else:
            return str(await ask(f"Plural of german `{self.back}`", example="Hunde"))

    @auto_column
    async def front_card(self) -> str:
        return (await self.emoji + " " if "words/" in self.deck else "") + (self.front or await self.translation)

    @auto_column
    async def back_card(self) -> str:
        return self.back if not await self.plural else f"{self.back} ({await self.plural})"


if __name__ == "__main__":
    from learn_language_magic.deps import Deps

    asyncio.run(
        autofill(
            row_cls=Vocabulary,
            database_id="1f38a3aab8c14da19bb1b4317bdbc148",
            notion_token=Deps.load().config.notion_token,
        )
    )
