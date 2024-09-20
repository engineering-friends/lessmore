import asyncio

from simple_scheduler.deps.deps import Deps
from telethon import TelegramClient


def main(env="test"):
    async def _main():
        # - Init deps

        deps = Deps.load(env=env)

    asyncio.run(_main())


if __name__ == "__main__":
    import fire

    fire.Fire(main)
