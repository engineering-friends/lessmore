from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from ef_bots.ef_threads.deps import Deps
from lessmore.utils.tested import tested
from teletalk.app import App
from teletalk.models.response import Response


if TYPE_CHECKING:
    from ef_bots.ef_threads.main import main


@tested([main] if TYPE_CHECKING else [])
class EfThreadsBot:
    def __init__(self, deps: Deps):
        self.deps = deps

    # - Context manager

    @staticmethod
    @asynccontextmanager
    async def stack(env: str):
        async with Deps(env=env) as deps:
            yield (
                EfThreadsBot(deps=deps),
                await App(
                    bot=deps.config.telegram_bot_token,
                    state_backend="rocksdict",
                    state_config={"path": str(deps.local_files_dir / "app_state")},
                ).__aenter__(),  # teletalk app
            )

    async def start(self, response: Response):
        await response.tell(
            """Привет!

Я буду пересылать тебе новые комментарии на твои посты, а также на посты, в которых ты принимаешь участие.

Чтобы отписаться от получения уведомлений о конкретном посте, просто поставь **любую** реакцию на пересланное сообщение в **этом** чате 💥

Попробуй оставить комментарий, чтобы посмотреть как это работает: https://t.me/c/2219948749/187?thread=185"""
        )
