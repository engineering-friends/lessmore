from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class ContextMiddleware(BaseMiddleware):
    def __init__(self, context):
        super().__init__()
        self.context = context

    async def __call__(self, handler, event: TelegramObject, data: dict):
        data["context"] = self.context
        return await handler(event, data)
