import time
import random
import pandas as pd
import pgpy
import os
import warnings

from hashlib import sha256
from cryptography import CryptographyDeprecationWarning
from datetime import datetime

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

CSV_SEPARATOR = ";"
SECONDS_IN_DAY = 86400
MAX_DAYS_BACK = 3

TRANSACTION_FILE_EXTENSION = ".csv"
ENCRYPTED_FILE_EXTENSION = "pgp"
APPLICATION_PREFIX_FILE_NAME = "ADE"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"

CHECKSUM_PREFIX = "#sha256sum:"

PERSON_NATURAL_LEGAL_RATIO = 3

CURRENCY_ISO4217 = "978"


class Transactionaggregate:
    """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Service"""

    def __init__(self, args):
        self.args = args

    def aggregate_transactions(self):
        """Produces a synthetic version of the CSV file produced by the sender for AdE

        Parameters:
          --aggr-qty: synthetic aggregates will be generated.
          --sender: ABI of the sender, default is "99999"
          --revers-ratio: the ratio between normal and reversal transactions
          -o, --out-dir: path to the directory where the file will be created, default is "."
          --pgp: if set also an encrypted version of the file is created
          --shuffle: if set the file lines are shuffled
          --ratio-no-pos-type: the ratio between know pos type and unknown ones
          --ratio-no-vat: the ratio between known and unknown VAT
        """

        if not self.args.aggr_qty:
            raise ValueError("--aggr-qty is mandatory")
        if self.args.sender and (len(self.args.sender) is not 5):
            raise ValueError("--sender must be of length 5")

        # Set the sender code (common to all aggregates)
        sender_code = self.args.sender

        # Set the transmission date (common to all aggregates)
        transmission_date = datetime.today().strftime('%Y-%m-%d')

        aggregates = []

        for i in range(self.args.aggr_qty):

            if self.args.reverse_ratio:
                operation_type = "01" if i % self.args.reverse_ratio == 0 else "00"
            else:
                operation_type = "00"

            # Set the accounting date from 0 to MAX_DAYS_BACK days back compared to transmission_date
            accounting_date = time.strftime('%Y-%m-%d', time.localtime(
                datetime.today().timestamp() - SECONDS_IN_DAY * random.randint(0, MAX_DAYS_BACK)))

            # Set random number of transactions
            num_trx = random.randint(1, 100)

            # Set random amount
            total_amount = random.randint(2000, 500000)

            merchant_id = sha256(f"merchant{i}".encode()).hexdigest()
            terminal_id = sha256(f"terminal{i}".encode()).hexdigest()

            fiscal_code = str(i).zfill(11)

            if self.args.ratio_dirty_vat:
                vat = "###na###" if (i + 2) % self.args.ratio_dirty_vat == 0 else str(i).zfill(11)
            else:
                vat = str(i).zfill(11)

            if self.args.ratio_dirty_pos_type:
                if (i + 3) % self.args.ratio_dirty_pos_type == 0:
                    pos_type = "99"
                else:
                    pos_type = "00"
            else:
                pos_type = "00"

            if self.args.to_ade:
                record_id = sha256(f"recordID{i}".encode()).hexdigest()
                aggregates.append(
                    [
                        record_id,
                        sender_code,
                        operation_type,
                        transmission_date,
                        accounting_date,
                        num_trx,
                        total_amount,
                        CURRENCY_ISO4217,
                        sender_code,
                        merchant_id,
                        terminal_id,
                        fiscal_code,
                        vat,
                        pos_type,
                    ]
                )
            else:
                aggregates.append(
                    [
                        sender_code,
                        operation_type,
                        transmission_date,
                        accounting_date,
                        num_trx,
                        total_amount,
                        CURRENCY_ISO4217,
                        sender_code,
                        merchant_id,
                        terminal_id,
                        fiscal_code,
                        vat,
                        pos_type,
                    ]
                )
        if self.args.to_ade:
            columns = [
                "record_ID",
                "sender_code",
                "operation_type",
                "transmission_date",
                "accounting_date",
                "num_trx",
                "total_amount",
                "currency",
                "sender_id",
                "merchant_id",
                "terminal_id",
                "fiscal_code",
                "vat",
                "pos_type"
            ]
        else:
            columns = [
                "sender_code",
                "operation_type",
                "transmission_date",
                "accounting_date",
                "num_trx",
                "total_amount",
                "currency",
                "sender_id",
                "merchant_id",
                "terminal_id",
                "fiscal_code",
                "vat",
                "pos_type"
            ]

        if self.args.shuffle:
            random.shuffle(aggregates)

        trx_df = pd.DataFrame(aggregates, columns=columns)
        trx_file_path = self.args.out_dir + "/" + APPLICATION_PREFIX_FILE_NAME + "." + str(
            sender_code) + "." + TRANSACTION_LOG_FIXED_SEGMENT + "." + datetime.today().strftime(
            '%Y%m%d.%H%M%S') + ".001" + TRANSACTION_FILE_EXTENSION

        os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

        with open(trx_file_path, "a") as f:
            # If the file is for AdE, there is no need to insert the hash at the beginning of it
            if not self.args.to_ade:
                csv_content = trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR, lineterminator="\n")
                f.write(CHECKSUM_PREFIX + sha256(
                    f"{csv_content}".encode()).hexdigest() + "\n")
            f.write(trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR))

        if self.args.pgp:
            # Encryption of transaction file
            with open(self.args.key) as public_key:
                pgp_key = public_key.read()
            if pgp_key is None:
                print("PGP public key is None")
                exit(1)

            pgp_file(trx_file_path, pgp_key)

        print(f"Done")


def pgp_file(file_path: str, pgp_key_data: str):
    key = pgpy.PGPKey.from_blob(pgp_key_data)
    with open(file_path, "rb") as f:
        message = pgpy.PGPMessage.new(f.read(), file=True)
    encrypted = key[0].encrypt(message, openpgp=True)
    output_path = f"{file_path}.{ENCRYPTED_FILE_EXTENSION}"
    with open(output_path, "wb") as f:
        f.write(bytes(encrypted))

    return output_path
