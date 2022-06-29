from hashlib import sha256
import time
import random
import uuid
import pandas as pd
import logging
import os
import gnupg
from tempfile import TemporaryDirectory
from datetime import datetime

CSV_SEPARATOR = ";"
PAN_UNENROLLED_PREFIX = "pan_unknown_"

SECONDS_IN_DAY = 86400
MAX_DAYS_BACK = 3

TRANSACTION_FILE_EXTENSION = ".csv"
ENCRYPTED_FILE_EXTENSION = ".pgp"
APPLICATION_PREFIX_FILE_NAME = "CSTAR"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"
CHECKSUM_PREFIX = "#sha256sum:"

PAYMENT_REVERSAL_RATIO = 100
POS_PHYSICAL_ECOMMERCE_RATIO = 5
PERSON_NATURAL_LEGAL_RATIO = 3
PAR_RATIO = 7

CURRENCY_ISO4217 = "978"
PAYMENT_CIRCUITS = [f"{i:02}" for i in range(11)]

OFFSETS = [
    ".000Z",
    ".000+01:00",
    ".000+0200",
    ".500+01:30"
]

MERCHANT_ID = "400000080205"
TERMINAL_ID = "80205005"
BIN = "40236010"
MCC = "4900"
FISCAL_CODE = "RSSMRA80A01H501U"
VAT = "12345678903"


class Transactionfilter:
    """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Service"""

    def __init__(self, args):
        self.args = args

    def synthetic_hashpans(self):
        """Produces a synthetic version of the CSV file obtainable from the RTD /hashed-pans endpoint

        Parameters:
          --pans-prefix: synthetic PANs will be generated as "{PREFIX}{NUMBER}"
          --haspans-qty: the number of hashpans to generate
          --salt: the salt to use when performing PAN hashing
        """
        if not self.args.pans_prefix:
            raise ValueError("--pans-prefix is mandatory")
        if not self.args.hashpans_qty:
            raise ValueError("--hashpans-qty is mandatory")
        if not self.args.salt:
            raise ValueError("--salt is mandatory")

        synthetic_pans = [
            f"{self.args.pans_prefix}{i}" for i in range(self.args.hashpans_qty)
        ]
        hpans = [
            sha256(f"{pan}{self.args.salt}".encode()).hexdigest()
            for pan in synthetic_pans
        ]
        hashpans_df = pd.DataFrame(hpans, columns=["hashed_pan"])
        print(hashpans_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR))

    def synthetic_transactions(self):
        """Produces a synthetic version of the CSV file produced by the senders for RTD

        Parameters:
          --pans-prefix: synthetic PANs will be generated as "{PREFIX}{NUMBER}"
          --pans-qty: the number of enrolled PANs to use in generated transactions
          --trx-qty: the number of transactions to generate in output
          --ratio: the ratio between transactions belonging to an enrolled PAN versus unenrolled (expressed as 1/ratio)
          --pos-number: how many different synthetic POS must be created
        """
        if not self.args.pans_prefix:
            raise ValueError("--pans-prefix is mandatory")
        if not self.args.pans_qty:
            raise ValueError("--pans-qty is mandatory")
        if not self.args.trx_qty:
            raise ValueError("--trx-qty is mandatory")
        if not self.args.ratio:
            raise ValueError("--ratio is mandatory")
        if not self.args.pos_number:
            raise ValueError("--pos-number is mandatory")

        # Set the sender code (common to all transactions)
        sender_code = self.args.sender

        synthetic_pans_enrolled = [
            f"{self.args.pans_prefix}{i}" for i in range(self.args.pans_qty)
        ]
        synthetic_pans_not_enrolled = [
            f"{PAN_UNENROLLED_PREFIX}{i}" for i in range(self.args.pans_qty)
        ]

        synthetic_pos = []
        for i in range(self.args.pos_number):
            synthetic_pos.append([
                str(1000000 + i),  # terminal_id
                str(2000000 + i),  # merchant_id,
                "CF" + str(3000000 + i),  # fiscal_code
                VAT if i % PERSON_NATURAL_LEGAL_RATIO == 0 else "",  # vat
                "00" if i % POS_PHYSICAL_ECOMMERCE_RATIO == 0 else "01",  # pos_type
            ])

        transactions = []

        for i in range(self.args.trx_qty):

            pos = random.choice(synthetic_pos)
            terminal_id = pos[0]
            merchant_id = pos[1]
            fiscal_code = pos[2]
            vat = pos[3]
            pos_type = pos[4]

            operation_type = "00"
            if i % PAYMENT_REVERSAL_RATIO == 0:
                operation_type = "01"

            if i % self.args.ratio == 0:
                pan = sha256(f"{random.choice(synthetic_pans_enrolled)}{self.args.salt}".encode()).hexdigest()
            else:
                pan = sha256(f"{random.choice(synthetic_pans_not_enrolled)}{self.args.salt}".encode()).hexdigest()

            id_trx_acquirer = uuid.uuid4().int
            id_trx_issuer = uuid.uuid4().int
            payment_circuit = random.choice(PAYMENT_CIRCUITS)

            # Set the transaction date from 0 to MAX_DAYS_BACK days back compared to transmission_date
            date_time = time.strftime('%Y-%m-%dT%H:%M:%S' + random.choice(OFFSETS), time.localtime(
                datetime.today().timestamp() - SECONDS_IN_DAY * random.random() * MAX_DAYS_BACK))

            correlation_id = ""
            if operation_type == "01":
                correlation_id = uuid.uuid4().int

            total_amount = random.randint(100, 100000)

            par = ""
            if i % PAR_RATIO == 0:
                par = str(uuid.uuid4())

            transactions.append(
                [
                    sender_code,
                    operation_type,
                    payment_circuit,
                    pan,
                    date_time,
                    id_trx_acquirer,
                    id_trx_issuer,
                    correlation_id,
                    total_amount,
                    CURRENCY_ISO4217,
                    sender_code,
                    merchant_id,
                    terminal_id,
                    BIN,
                    MCC,
                    fiscal_code,
                    vat,
                    pos_type,
                    par,
                ]
            )

        columns = [
            "sender_code",
            "operation_type",
            "circuit_type",
            "hpan",
            "date_time",
            "id_trx_acquirer",
            "id_trx_issuer",
            "correlation_id",
            "total_amount",
            "currency",
            "sender_id",
            "merchant_id",
            "terminal_id",
            "bin",
            "mcc",
            "fiscal_code",
            "vat",
            "pos_type",
            "par",
        ]
        trx_df = pd.DataFrame(transactions, columns=columns)
        trx_file_path = self.args.out_dir + "/" + APPLICATION_PREFIX_FILE_NAME + "." + str(
            sender_code) + "." + TRANSACTION_LOG_FIXED_SEGMENT + "." + datetime.today().strftime(
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
        file_extension: str = ENCRYPTED_FILE_EXTENSION,
) -> None:
    """Encrypt a file using provided encryption key.

    :param file_path: path of file to be encrypted
    :type file_path: str
    :param encryption_key: path of the key file to use
    :type encryption_key: str
    :param remove_plaintext: remove plaintext file after encryption? Defaults to False
    :type remove_plaintext: bool
    :param file_extension: extension to add to encrypted files. Defaults to '.pgp'
    :type file_extension: str
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
