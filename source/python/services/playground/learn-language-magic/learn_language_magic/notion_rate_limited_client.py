import asyncio

from typing import Any, Dict, Optional

from lessmore.utils.asynchronous.async_rate_limiter import AsyncRateLimiter
from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient
from loguru import logger


RATE_LIMITER = AsyncRateLimiter(rate=3, period_seconds=1)


class NotionRateLimitedClient(EnrichedNotionAsyncClient):
    async def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
    ) -> Any:
        # - Acquire

        await RATE_LIMITER.acquire()

        # - Return

        try:
            return await super().request(path, method, query, body, auth)
        except Exception as e:
            if "conflict" in str(e):
                await asyncio.sleep(1)
                logger.debug("Conflict error, retrying", e=e)
                return await self.request(path, method, query, body, auth)
            else:
                raise
