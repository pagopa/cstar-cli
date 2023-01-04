import dataclasses
from typing import Optional

import requests


@dataclasses.dataclass
class RtdApiEnvironment:
    base_url: str
    api_key: str
    private_key_path: str
    certificate_path: str


@dataclasses.dataclass
class SasResponse:
    sas: str
    container: str


class RtdApi:

    def __init__(self, config: RtdApiEnvironment):
        self.config = config
        self.cert = (config.certificate_path, config.private_key_path)

    def upload_file(self, file_path: str, sas: str, container_name: str, file_name: str) -> bool:
        with open(file_path, 'rb') as f:
            response = requests.put(
                f"{self.config.base_url}pagopastorage/{container_name}/{file_name}?{sas}",
                cert=self.cert,
                data=f,
                headers={
                    "Ocp-Apim-Subscription-Key": self.config.api_key,
                    "Content-Type": "application/octet-stream",
                    "x-ms-blob-type": "BlockBlob",
                    "x-ms-version": "2021-08-06"
                },
            )
            return 200 <= response.status_code < 300

    def get_sas(self) -> Optional[SasResponse]:
        response = requests.post(
            f"{self.config.base_url}rtd/csv-transaction/rtd/sas",
            cert=self.cert,
            headers={
                "Ocp-Apim-Subscription-Key": self.config.api_key
            }
        )
        if 200 <= response.status_code < 300:
            json = response.json()
            return SasResponse(
                json["sas"],
                json["authorizedContainer"]
            )
        else:
            return None

    def get_public_key(self):
        response = requests.get(
            f"{self.config.base_url}rtd/csv-transaction/publickey",
            cert=self.cert,
            headers={
                "Ocp-Apim-Subscription-Key": self.config.api_key
            }
        )
        return response.text if 200 <= response.status_code < 300 else None
