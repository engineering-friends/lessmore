import asyncio

from typing import Any, Dict, Optional

from lessmore.utils.asynchronous.async_rate_limiter import AsyncRateLimiter
from lessmore.utils.enriched_notion_client.enriched_notion_client import EnrichedNotionAsyncClient


RATE_LIMITER = AsyncRateLimiter(rate=3, period=1)


CREATE_PAGE_LOCK = asyncio.Lock()


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

        # - Lock if creating a page

        if path == "pages":
            async with CREATE_PAGE_LOCK:
                return await super().request(path, method, query, body, auth)

        # - Return

        return await super().request(path, method, query, body, auth)
