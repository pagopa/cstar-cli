import hashlib
import logging
import os.path
import tempfile

from typing import Optional

import gnupg
from .rtd_api import RtdApiEnvironment, RtdApi


class TransactionUpload:
    api_urls = {
        "dev": "https://api.dev.cstar.pagopa.it/",
        "uat": "https://api.uat.cstar.pagopa.it/",
        "prod": "https://api.cstar.pagopa.it/"
    }

    def __init__(self, args):
        self.args = args
        self.api = RtdApi(RtdApiEnvironment(
            base_url=TransactionUpload.api_urls[args.env],
            api_key=self.args.api_key,
            private_key_path=self.args.key,
            certificate_path=self.args.cert
        ))
        self.api_key = self.args.api_key

    def upload(self):
        upload_file = self.args.file
        if not upload_file.endswith(".pgp"):
            pgp_key = self.api.get_public_key()
            upload_file = self._pgp(upload_file, pgp_key)
        upload_file_name = os.path.basename(upload_file)

        sas_response = self.api.get_sas()

        print(f"Uploading {upload_file}, with name {upload_file_name} to {sas_response.container}")
        result = self.api.upload_file(
            file_path=upload_file,
            file_name=upload_file_name,
            sas=sas_response.sas,
            container_name=sas_response.container
        )
        print(f"Upload {'success' if result else 'failed'}")

    def _pgp(self, file_path: str, pgp_key_data: str) -> Optional[str]:
        with tempfile.TemporaryDirectory() as temp_gpg_home:
            gpg = gnupg.GPG(gnupghome=temp_gpg_home)
            import_result = gpg.import_keys(pgp_key_data)
            logging.info(f"GPG import keys: {import_result.results}")
            output_path = f"{file_path}.pgp"
            with open(file_path, "rb") as f:
                status = gpg.encrypt_file(
                    f,
                    recipients=import_result.results[0]["fingerprint"],
                    output=output_path,
                    extra_args=["--openpgp", "--trust-model", "always"],
                    armor=False,
                )
                if status.ok:
                    return output_path
                else:
                    logging.error("Failed to pgp")
        return None
