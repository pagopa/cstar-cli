import logging
import os
import tempfile

import pgpy
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


def serialize(dataset, columns, destination_path, have_header=False):
    dataset_dataframe = pd.DataFrame(dataset, columns=columns)
    trx_file_path = os.path.join(destination_path, )

    os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

    with open(trx_file_path, "a", newline='') as f:
        f.write(dataset_dataframe.to_csv(index=False, header=have_header, sep=CSV_SEPARATOR))


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
    key = pgpy.PGPKey.from_blob(pgp_key_data)
    message = pgpy.PGPMessage.new(payload)
    ciphertext = key[0].encrypt(message,version=b'BCPG v1.58')
    return str(ciphertext)

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
