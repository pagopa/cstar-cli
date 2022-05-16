import time
from hashlib import sha256
import random

import pandas as pd
import logging
import os
import gnupg
from tempfile import TemporaryDirectory
from datetime import datetime

CSV_SEPARATOR = ";"
SECONDS_IN_DAY = 86400
MAX_DAYS_BACK = 3

TRANSACTION_FILE_EXTENSION = ".csv"
ENCRYPTED_FILE_EXTENSION = ".pgp"
APPLICATION_PREFIX_FILE_NAME = "ADE"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"

CHECKSUM_PREFIX = "#sha256sum:"

POS_PHYSICAL_ECOMMERCE_RATIO = 5
PERSON_NATURAL_LEGAL_RATIO = 3

ACQUIRER_ID = "09509"
CURRENCY_ISO4217 = "978"

class Transactionaggregate:
    """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Acquirer"""

    def __init__(self, args):
        self.args = args

    def aggregate_transactions(self):
        """Produces a synthetic version of the CSV file produced by the acquirers for AdE

        Parameters:
          --aggr-qty: synthetic aggregates will be generated.
          --acquirer: ABI of the acquirer, default is "99999"
          --revers-ratio: the ratio between normal and reversal transactions
          -o, --out-dir: path to the directory where the file will be created, default is "."
          --pgp: if set also an encrypted version of the file is created
          --shuffle: if set the file lines are shuffled
          --ratio-no-pos-type: the ratio between know pos type and unknown ones
          --ratio-no-vat: the ratio between known and unknown VAT
        """

        if not self.args.aggr_qty:
            raise ValueError("--aggr-qty is mandatory")

        # Set the acquirer code (common to all aggregates)
        acquirer_code = self.args.acquirer

        # Set the transmission date (common to all aggregates)
        transmission_date = datetime.today().strftime('%Y-%m-%d')

        transactions = []

        for i in range(self.args.aggr_qty):

            if i % self.args.revers_ratio == 0:
                operation_type = "01"
            else:
                operation_type = "00"

            # Set the accounting date from 0 to MAX_DAYS_BACK days back compared to transmission_date
            accounting_date = time.strftime('%Y-%m-%d', time.localtime(
                datetime.today().timestamp() - SECONDS_IN_DAY * random.randint(0, MAX_DAYS_BACK)))

            # Set random number of transactions
            num_trx = random.randint(1, 100)

            # Set random amount
            total_amount = random.randint(2000, 500000)

            merchant_id = abs(hash(sha256(f"merchant{i}".encode()).hexdigest()))
            terminal_id = abs(hash(sha256(f"terminal{i}".encode()).hexdigest()))

            fiscal_code = str(i).zfill(11)

            if self.args.ratio_no_vat:
                vat = "###na###" if i % self.args.ratio_no_vat == 0 else str(i).zfill(11)
            else:
                vat = str(i).zfill(11)

            if self.args.ratio_no_pos_type:
                if i % self.args.ratio_no_pos_type == 0:
                    pos_type = "127"
                elif i % POS_PHYSICAL_ECOMMERCE_RATIO == 0:
                    pos_type = "00"
                else:
                    pos_type = "01"
            else:
                pos_type = "00" if i % POS_PHYSICAL_ECOMMERCE_RATIO == 0 else "01"

            transactions.append(
                [
                    acquirer_code,
                    operation_type,
                    transmission_date,
                    accounting_date,
                    num_trx,
                    total_amount,
                    CURRENCY_ISO4217,
                    ACQUIRER_ID,
                    merchant_id,
                    terminal_id,
                    fiscal_code,
                    vat,
                    pos_type,
                ]
            )

        columns = [
            "acquirer_code",
            "operation_type",
            "transmission_date",
            "accounting_date",
            "num_trx",
            "total_amount",
            "currency",
            "acquirer_id",
            "merchant_id",
            "terminal_id",
            "fiscal_code",
            "vat",
            "pos_type"
        ]

        if self.args.shuffle:
            random.shuffle(transactions)

        trx_df = pd.DataFrame(transactions, columns=columns)
        trx_file_path = self.args.out_dir + "/" + APPLICATION_PREFIX_FILE_NAME + "." + str(
            acquirer_code) + "." + TRANSACTION_LOG_FIXED_SEGMENT + "." + datetime.today().strftime(
            '%Y%m%d.%H%M%S') + ".001" + TRANSACTION_FILE_EXTENSION

        os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

        with open(trx_file_path, "a") as f:
            f.write(CHECKSUM_PREFIX + sha256(
                f"{trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR)}".encode()).hexdigest() + "\n")
            f.write(trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR))

        if self.args.pgp:
            encrypt_file(trx_file_path, self.args.key)

        print(f"Done")


def encrypt_file(
        file_path: str,
        encryption_key: str,
        *,
        remove_plaintext: bool = False,
) -> None:
    """Encrypt a file using provided encryption key.

    :param file_path: path of file to be encrypted
    :type file_path: str
    :param encryption_key: path of the key file to use
    :type encryption_key: str
    :param remove_plaintext: remove plaintext file after encryption? Defaults to False
    :type remove_plaintext: bool
    :raises RuntimeError:
    """
    with TemporaryDirectory() as temp_gpg_home:
        logging.debug(f"Setting temporary GPG home to {temp_gpg_home}")
        gpg = gnupg.GPG(gnupghome=temp_gpg_home)
        key_data = open(encryption_key).read()
        import_result = gpg.import_keys(key_data)
        logging.info(f"GPG import keys: {import_result.results}")
        with open(file_path, "rb") as f:
            status = gpg.encrypt_file(
                file=f,
                recipients=import_result.results[0]["fingerprint"],
                output=f"{file_path}{ENCRYPTED_FILE_EXTENSION}",
                extra_args=["--openpgp", "--trust-model", "always"],
                armor=False,
            )
        if status.ok:
            if remove_plaintext:
                os.remove(file_path)
            logging.info(f"Encrypted file as {file_path}{ENCRYPTED_FILE_EXTENSION}")
        else:
            logging.info(f"Failed to encrypt")
            raise RuntimeError(status)
