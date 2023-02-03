import os
import random
import uuid
import warnings

from cryptography import CryptographyDeprecationWarning
from .idpay_utilities import serialize, is_iso8601, flatten, flatten_values, pgp_file, pgp_string
from .idpay_api import IDPayApiEnvironment, IDPayApi
from hashlib import sha256
from datetime import datetime
from dateutil import parser
from faker import Faker

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

circuits = ['visa', 'mastercard', 'maestro', 'amex']

mcc_blacklist = ['4784', '6010', '6011', '7995', '9222', '9311']

fake = Faker('it_IT')
fc_columns = [
    "FC"
]
fc_pan_columns = [
    "FC",
    "PAN"
]
fc_hpan_columns = [
    "FC",
    "HPAN"
]
pan_hpan_columns = [
    "PAN",
    "HPAN"
]
fc_pgppan_columns = [
    "FC",
    "PGPPAN"
]
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
pans_columns = [
    "pan"
]
hpans_columns = [
    "hpan"
]
TRANSACTION_FILE_EXTENSION = "csv"
APPLICATION_PREFIX_FILE_NAME = "CSTAR"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"
CHECKSUM_PREFIX = "#sha256sum:"


def fake_pan(num_pan):
    fake_credit_cards = set()

    while len(fake_credit_cards) < num_pan:
        fake_credit_cards.add(fake.credit_card_number(random.choice(circuits)))

    return fake_credit_cards


def fake_fc(num_fc):
    fake_fiscal_codes = set()

    while len(fake_fiscal_codes) < num_fc:
        tmp_fc = fake.ssn()
        fake_fiscal_codes.add(f'{tmp_fc[:11]}X000{tmp_fc[15:]}')

    return fake_fiscal_codes


def fc_pan_couples(num_fc, min_pan_per_fc, max_pan_per_fc):
    if min_pan_per_fc > max_pan_per_fc:
        print("Error: minimum credit cards per fiscal code greater than maximum credit cards per fiscal code")
        exit(1)

    fc_pan = {}

    fiscal_codes = fake_fc(num_fc)

    for fc in fiscal_codes:
        fc_pan[fc] = set()
        tmp_num_pan_per_fc = random.randint(min_pan_per_fc, max_pan_per_fc)
        fc_pan[fc] = fake_pan(tmp_num_pan_per_fc)

    return fc_pan


def fc_hpans_couples(fc_pan, salt):
    fc_hpans = {}

    for fc in fc_pan.keys():
        fc_hpans[fc] = set()
        for pan in fc_pan[fc]:
            fc_hpans[fc].add(sha256(f"{pan}{salt}".encode()).hexdigest())

    return fc_hpans


def pan_hpans_couples(pan, salt):
    pan_hpans = {}

    for pan in pan:
        pan_hpans[pan] = set()
        pan_hpans[pan].add(sha256(f"{pan}{salt}".encode()).hexdigest())

    return pan_hpans


def fc_pgpans_couples(fc_pan, key):
    fc_pgppans = {}

    for fc in fc_pan.keys():
        fc_pgppans[fc] = set()
        for pan in fc_pan[fc]:
            fc_pgppans[fc].add(
                (pgp_string(pan, key).replace("\'", "").replace("\n", "\\n")))

    return fc_pgppans


def input_trx_name_formatter(sender_code, trx_datetime):
    return "{}.{}.{}.{}.001.01.{}".format(APPLICATION_PREFIX_FILE_NAME, sender_code, TRANSACTION_LOG_FIXED_SEGMENT,
                                          parser.parse(trx_datetime).strftime('%Y%m%d.%H%M%S'),
                                          TRANSACTION_FILE_EXTENSION)


class IDPayDataset:
    def __init__(self, args):
        self.args = args
        self.api = IDPayApi(IDPayApiEnvironment(
            base_url=IDPayApi.rtd_api_urls[args.env],
            api_key=self.args.api_key,
            private_key_path=self.args.key,
            certificate_path=self.args.cert
        ))
        self.api_key = self.args.api_key

    def dataset_and_transactions(self):
        fc_pan = fc_pan_couples(self.args.num_fc, self.args.min_pan_per_fc, self.args.max_pan_per_fc)
        with open(self.args.PM_pubk) as public_key:
            fc_pgpans = fc_pgpans_couples(fc_pan, public_key.read())

        if self.args.PM_salt is None:
            pm_salt = self.api.get_salt()
        else:
            pm_salt = self.args.PM_salt

        if pm_salt is None:
            print("Salt is None")
            exit(1)

        if not is_iso8601(self.args.datetime):
            print(f'Error: {self.args.datetime} is not ISO8601')
            exit(1)

        if self.args.mcc in mcc_blacklist:
            print(f'Error: {self.args.mcc} is in blacklist {mcc_blacklist}')
            exit(1)

        transactions = []
        correlation_ids = set()
        ids_trx_acq = set()

        for fc in fc_pan.keys():
            for i in range(self.args.trx_per_fc):
                curr_pan = random.choice(list(fc_pan[fc]))

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

                transactions.append(
                    [
                        self.args.sender_code,  # sender code
                        "00",  # operation type
                        "00",  # circuit
                        sha256(f"{curr_pan}{pm_salt}".encode()).hexdigest(),  # HPAN
                        parser.parse(self.args.datetime).strftime('%Y-%m-%dT%H:%M:%S.000Z'),  # datetime
                        curr_id_trx_acq,  # id_trx_acquirer
                        uuid.uuid4().int,  # id_trx_issuer
                        curr_correlation_id,  # correlation_id
                        random.randint(self.args.min_amount, self.args.max_amount),  # amount
                        "978",
                        self.args.acquirer_code,  # Acquirer id
                        uuid.uuid4().int,  # merchant_id
                        uuid.uuid4().int,  # terminal id
                        curr_pan[:6],  # BIN
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
                                         input_trx_name_formatter(self.args.sender_code, self.args.datetime))

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

        pgp_file(transactions_path, pgp_key)

        serialize(flatten(fc_pgpans), fc_pgppan_columns,
                  os.path.join(curr_output_path, 'fc_pgpans.csv'))
        serialize(flatten_values(fc_pan), pans_columns, os.path.join(curr_output_path, 'pans.csv'))

        serialize(flatten_values(fc_hpans_couples(fc_pan, pm_salt)), hpans_columns,
                  os.path.join(curr_output_path, 'hpans.csv'))

        pan_hpans = pan_hpans_couples(flatten_values(fc_pan), pm_salt)

        serialize(flatten(pan_hpans), pan_hpan_columns,
                  os.path.join(curr_output_path, 'pan_hpans.csv'))
