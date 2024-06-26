import asyncio

from typing import Literal

import fire

from discord_to_telegram_forwarder.main import main


def run(env: Literal["test", "prod"]):
    asyncio.run(main(env=env))


if __name__ == "__main__":
    fire.Fire(run)
