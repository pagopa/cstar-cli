import asyncio
import time

import aiohttp


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

    async def tokenize(self, fc: str) -> str:
        await self.limiter.wait_for_token()
        tokenization_response = await self.session.request(
            method='PUT',
            url=f'https://api.{self.env}.tokenizer.pdv.pagopa.it/tokenizer/v1/tokens',
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
