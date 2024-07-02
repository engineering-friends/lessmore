from typing import Any, Dict, Optional

from lessmore.utils.enriched_notion_client import EnrichedNotionAsyncClient
from lessmore.utils.rate_limiter import RateLimiter


RATE_LIMITER = RateLimiter(rate=3, period=1)


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

        return await super().request(path, method, query, body, auth)
