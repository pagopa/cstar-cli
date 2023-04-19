import os
import random
import uuid
import warnings

from cryptography import CryptographyDeprecationWarning

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

from .idpay_utilities import serialize, is_iso8601, pgp_file, deserialize, random_date, deserialize_trx
from .idpay_api import IDPayApiEnvironment, IDPayApi
from hashlib import sha256
from datetime import datetime
from dateutil import parser
from faker import Faker

mcc_blacklist = ['4784', '6010', '6011', '7995', '9222', '9311']

fake = Faker('it_IT')

transaction_columns = [
    "sender_code",
    "operation_type",
    "circuit_type",
    "pan",
    "date_time",
    "id_trx_acquirer",
    "id_trx_issuer",
    "correlation_id",
    "total_amount",
    "currency",
    "acquirer_id",
    "merchant_id",
    "terminal_id",
    "bin",
    "mcc",
    "fiscal_code",
    "vat",
    "pos_type",
    "par",
]

TRANSACTION_FILE_EXTENSION = "csv"
APPLICATION_PREFIX_FILE_NAME = "CSTAR"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"
CHECKSUM_PREFIX = "#sha256sum:"


def input_trx_name_formatter(sender_code, trx_datetime):
    return "{}.{}.{}.{}.001.01.{}".format(APPLICATION_PREFIX_FILE_NAME, sender_code, TRANSACTION_LOG_FIXED_SEGMENT,
                                          parser.parse(trx_datetime).strftime('%Y%m%d.%H%M%S'),
                                          TRANSACTION_FILE_EXTENSION)


class IDPayTransactions:
    def __init__(self, args):
        self.args = args
        self.api = IDPayApi(IDPayApiEnvironment(
            base_url=IDPayApi.rtd_api_urls[args.env],
            api_key=self.args.api_key,
            private_key_path=self.args.key,
            certificate_path=self.args.cert
        ))
        self.api_key = self.args.api_key

    def transactions(self):

        transactions = []
        correlation_ids = set()
        ids_trx_acq = set()

        if not is_iso8601(self.args.start_datetime):
            print(f'Error: {self.args.start_datetime} is not ISO8601')
            exit(1)

        if self.args.end_datetime is None:
            self.args.end_datetime = self.args.start_datetime

        if not is_iso8601(self.args.end_datetime):
            print(f'Error: {self.args.end_datetime} is not ISO8601')
            exit(1)

        if self.args.mcc in mcc_blacklist:
            print(f'Error: {self.args.mcc} is in blacklist {mcc_blacklist}')
            exit(1)

        synthetic_hpans_deserialized = deserialize(self.args.input_pans_hashpans)
        if self.args.hpans_head is None:
            num_wanted_hpans = len(synthetic_hpans_deserialized)
        else:
            num_wanted_hpans = self.args.hpans_head

        synthetic_hpans_enrolled = list(synthetic_hpans_deserialized.items())[:num_wanted_hpans]

        if len(synthetic_hpans_enrolled) == 0:
            print("The hashpan file must not be empty")
            exit(1)

        for fc in range(self.args.trx_qty):
            curr_pan = random.choice(synthetic_hpans_enrolled)

            # Ensure Correlation ID uniqueness
            curr_correlation_id = uuid.uuid4().int
            while curr_correlation_id in correlation_ids:
                curr_correlation_id = uuid.uuid4().int
            correlation_ids.add(curr_correlation_id)

            # Ensure ID trx acquirer uniqueness
            curr_id_trx_acq = uuid.uuid4().int
            while curr_id_trx_acq in ids_trx_acq:
                curr_id_trx_acq = uuid.uuid4().int
            ids_trx_acq.add(curr_id_trx_acq)

            curr_datetime = random_date(parser.parse(self.args.start_datetime),
                                        parser.parse(self.args.end_datetime))

            transactions.append(
                [
                    self.args.sender_code,  # sender code
                    "00",  # operation type
                    "00",  # circuit
                    curr_pan[1],  # HPAN
                    curr_datetime.strftime('%Y-%m-%dT%H:%M:%S.000Z'),  # datetime
                    curr_id_trx_acq,  # id_trx_acquirer
                    uuid.uuid4().int,  # id_trx_issuer
                    curr_correlation_id,  # correlation_id
                    random.randint(self.args.min_amount, self.args.max_amount),  # amount
                    "978",
                    self.args.acquirer_code,  # Acquirer id
                    uuid.uuid4().int,  # merchant_id
                    uuid.uuid4().int,  # terminal id
                    curr_pan[0][:6],  # BIN
                    self.args.mcc,  # MCC
                    fake.ssn(),  # Fiscal Code
                    fake.company_vat().replace("IT", ""),  # VAT
                    "00",  # POS type
                    sha256(f"{curr_pan}".encode()).hexdigest().upper()[:29]
                    # PAR (this is not the way a PAR is calculated)
                ]
            )

        # Serialization
        random.shuffle(transactions)

        curr_output_path = os.path.join(self.args.out_dir, str(datetime.now().strftime('%Y%m%d-%H%M%S')))

        transactions_path = os.path.join(curr_output_path,
                                         input_trx_name_formatter(self.args.sender_code, self.args.start_datetime))

        serialize(transactions, transaction_columns, transactions_path)

        # Add checksum header to simulate Batch Service
        with open(transactions_path, 'r+', newline='') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(CHECKSUM_PREFIX + sha256(str(transactions).encode()).hexdigest() + '\n' + content)

        # Encryption of transaction file
        if self.args.RTD_pubk is None:
            pgp_key = self.api.get_pgp_public_key()
        else:
            with open(self.args.RTD_pubk) as public_key:
                pgp_key = public_key.read()

        if pgp_key is None:
            print("PGP public key is None")
            exit(1)
        pgp_file(transactions_path, pgp_key)

    def defined_transactions(self):

        transactions = []
        correlation_ids = set()
        ids_trx_acq = set()

        if not is_iso8601(self.args.start_datetime):
            print(f'Error: {self.args.start_datetime} is not ISO8601')
            exit(1)

        if self.args.end_datetime is None:
            self.args.end_datetime = self.args.start_datetime

        if not is_iso8601(self.args.end_datetime):
            print(f'Error: {self.args.end_datetime} is not ISO8601')
            exit(1)

        if self.args.mcc in mcc_blacklist:
            print(f'Error: {self.args.mcc} is in blacklist {mcc_blacklist}')
            exit(1)

        synthetic_hpans_deserialized = deserialize_trx(self.args.input_hashpans_amounts)

        for curr_hpan in synthetic_hpans_deserialized.items():
            for amount in curr_hpan[1]:
                # Ensure Correlation ID uniqueness
                curr_correlation_id = uuid.uuid4().int
                while curr_correlation_id in correlation_ids:
                    curr_correlation_id = uuid.uuid4().int
                correlation_ids.add(curr_correlation_id)

                # Ensure ID trx acquirer uniqueness
                curr_id_trx_acq = uuid.uuid4().int
                while curr_id_trx_acq in ids_trx_acq:
                    curr_id_trx_acq = uuid.uuid4().int
                ids_trx_acq.add(curr_id_trx_acq)

                curr_datetime = random_date(parser.parse(self.args.start_datetime),
                                            parser.parse(self.args.end_datetime))
                transactions.append(
                    [
                        self.args.sender_code,  # sender code
                        "00",  # operation type
                        "00",  # circuit
                        curr_hpan[0],  # HPAN
                        curr_datetime.strftime('%Y-%m-%dT%H:%M:%S.000+01:00'),  # datetime
                        curr_id_trx_acq,  # id_trx_acquirer
                        uuid.uuid4().int,  # id_trx_issuer
                        curr_correlation_id,  # correlation_id
                        amount,  # amount
                        "978",
                        self.args.acquirer_code,  # Acquirer id
                        uuid.uuid4().int,  # merchant_id
                        uuid.uuid4().int,  # terminal id
                        '999999',  # BIN
                        self.args.mcc,  # MCC
                        'RSSMRA80A01H501U',  # Merchant Fiscal Code
                        fake.company_vat().replace("IT", ""),  # VAT
                        "00",  # POS type
                        sha256(f"{curr_hpan[0]}".encode()).hexdigest().upper()[:29]
                        # PAR (this is not the way a PAR is calculated)
                    ]
                )

        # Serialization
        curr_output_path = os.path.join(self.args.out_dir, str(datetime.now().strftime('%Y%m%d-%H%M%S')))

        transactions_path = os.path.join(curr_output_path,
                                         input_trx_name_formatter(self.args.sender_code, self.args.end_datetime))

        serialize(transactions, transaction_columns, transactions_path)

        # Add checksum header to simulate Batch Service
        with open(transactions_path, 'r+', newline='') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(CHECKSUM_PREFIX + sha256(str(transactions).encode()).hexdigest() + '\n' + content)

        # Encryption of transaction file
        if self.args.RTD_pubk is None:
            pgp_key = self.api.get_pgp_public_key()
        else:
            with open(self.args.RTD_pubk) as public_key:
                pgp_key = public_key.read()

        if pgp_key is None:
            print("PGP public key is None")
            exit(1)
        pgp_file(transactions_path, pgp_key)
