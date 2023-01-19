import io
import logging
import os
import tempfile

import gnupg
import pandas as pd
from dateutil import parser

CSV_SEPARATOR = ";"

def is_iso8601(date_to_check):
    try:
        parser.parse(date_to_check)
        return True
    except ValueError:
        return False
def serialize(dataset, columns, destination_path):
    dataset_dataframe = pd.DataFrame(dataset, columns=columns)
    trx_file_path = os.path.join(destination_path, )

    os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

    with open(trx_file_path, "a") as f:
        f.write(dataset_dataframe.to_csv(index=False, header=False, sep=CSV_SEPARATOR))


def flatten(dataset):
    res = []
    for i in dataset:
        for j in dataset[i]:
            res.append([i, j])
    return res


def flatten_values(dataset):
    res = []
    for i in dataset:
        for j in dataset[i]:
            res.append(j)
    return res

def pgp_string(payload: str, pgp_key_data: str):
    with tempfile.TemporaryDirectory() as temp_gpg_home:
        gpg = gnupg.GPG(gnupghome=temp_gpg_home)
        import_result = gpg.import_keys(pgp_key_data)
        with io.StringIO(payload) as to_be_encrypted:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pgp', mode='r+b') as f:
                status = gpg.encrypt_file(
                    to_be_encrypted,
                    recipients=import_result.results[0]["fingerprint"],
                    output=f.name,
                    extra_args=["--openpgp", "--trust-model", "always"],
                    armor=True,
                )
                if status.ok:
                    f.seek(0)
                    return f.read()
                else:
                    logging.error("Failed to pgp")
    return None

def pgp_file(file_path: str, pgp_key_data: str):
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
