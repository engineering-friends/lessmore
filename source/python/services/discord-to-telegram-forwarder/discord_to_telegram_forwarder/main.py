from typing import Literal

import fire

from discord_to_telegram_forwarder.run import run


def main(env: Literal["test", "prod"]):
    run(env=env)


if __name__ == "__main__":
    fire.Fire(main)
