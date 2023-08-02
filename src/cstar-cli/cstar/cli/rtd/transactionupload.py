import os.path
import pgpy
import warnings

from .rtd_api import RtdApiEnvironment, RtdApi

warnings.filterwarnings("ignore")

ENCRYPTED_FILE_EXTENSION = "pgp"


def pgp_file(file_path: str, pgp_key_data: str):
    key = pgpy.PGPKey.from_blob(pgp_key_data)
    with open(file_path, "rb") as f:
        message = pgpy.PGPMessage.new(f.read(), file=True)
    encrypted = key[0].encrypt(message, openpgp=True)
    output_path = f"{file_path}.{ENCRYPTED_FILE_EXTENSION}"
    with open(output_path, "wb") as f:
        f.write(bytes(encrypted))

    return output_path


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
            upload_file = pgp_file(upload_file, pgp_key)
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
