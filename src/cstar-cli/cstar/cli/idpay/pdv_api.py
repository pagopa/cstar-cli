import aiohttp


class PdvApi:

    def __init__(self, env: str, api_key: str, session: aiohttp.client.ClientSession):
        self.session = session
        self.env = env
        self.api_key = api_key

    async def tokenize(self, fc: str) -> aiohttp.client.ClientResponse:
        return await self.session.request(
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
