import dataclasses
import httpx

@dataclasses.dataclass
class IDPayApiEnvironment:
    base_url: str
    api_key: str
    private_key_path: str
    certificate_path: str


class IDPayApi:

    rtd_api_urls = {
        "dev": "https://api.dev.cstar.pagopa.it/",
        "uat": "https://api.uat.cstar.pagopa.it/",
        "prod": "https://api.cstar.pagopa.it/"
    }

    def __init__(self, config: IDPayApiEnvironment):
        self.config = config
        self.cert = (config.certificate_path, config.private_key_path)

    def get_salt(self):
        response = httpx.get(
            f"{self.config.base_url}rtd/payment-instrument-manager/salt",
            cert=self.cert,
            headers={
                "Ocp-Apim-Subscription-Key": self.config.api_key
            }
        )
        return response.text if 200 <= response.status_code < 300 else None
