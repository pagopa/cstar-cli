import asyncio
import logging
import time

import aiohttp

logger = logging.getLogger(__name__)


# Simple token bucket
class RateLimiter:
    def __init__(self, rps: int, max_tokens: int):
        self.rps = rps
        self.available_tokens = max_tokens
        self.max_tokens = max_tokens
        self.updated_at = time.monotonic()

    async def wait_for_token(self):
        while self.available_tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        self.available_tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        diff_from_last_token_update = now - self.updated_at
        new_tokens = diff_from_last_token_update * self.rps
        if self.available_tokens + new_tokens >= 1:
            self.available_tokens = min(self.available_tokens + new_tokens, self.max_tokens)  # clamp to max_tokens
            self.updated_at = now


class PdvApi:
    # DEV and UAT share the same url
    _PDV_BASE_URL = {
        "dev": "https://api.uat.tokenizer.pdv.pagopa.it",
        "uat": "https://api.uat.tokenizer.pdv.pagopa.it",
        "prod": "https://api.tokenizer.pdv.pagopa.it"
    }

    def __init__(
            self,
            env: str,
            api_key: str,
            session: aiohttp.client.ClientSession,
            rate_limit_per_sec: int
    ):
        self.session = session
        self.env = env
        self.api_key = api_key
        self.limiter = RateLimiter(rate_limit_per_sec, rate_limit_per_sec)
        self.base_url = self._PDV_BASE_URL[self.env]
        if self.env == "dev":
            logger.warning("Detect PDV usage with DEV environment. DEV and UAT environment share the same url")

    async def tokenize(self, fc: str) -> str:
        await self.limiter.wait_for_token()
        tokenization_response = await self.session.request(
            method='PUT',
            url=f'{self.base_url}/tokenizer/v1/tokens',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': self.api_key,
            },
            json={
                'pii': fc
            },
            timeout=5000
        )
        assert tokenization_response.status == 200
        return (await tokenization_response.json())['token']
