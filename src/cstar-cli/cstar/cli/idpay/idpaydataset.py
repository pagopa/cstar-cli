import os
import random
import uuid
from .idpay_api import IDPayApiEnvironment, IDPayApi
from hashlib import sha256

import pandas as pd
from dateutil import parser

from faker import Faker

circuits = ['visa', 'mastercard', 'maestro', 'amex']

mcc_blacklist = ['4784', '6010', '6011', '7995', '9222', '9311']

fake = Faker('it_IT')
fc_columns = [
    "FC"
]
fc_cc_columns = [
    "FC",
    "CC"
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
CSV_SEPARATOR = ";"
TRANSACTION_FILE_EXTENSION = "csv"
ENCRYPTED_FILE_EXTENSION = "pgp"
APPLICATION_PREFIX_FILE_NAME = "CSTAR"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"


def fake_cc(num_cc):
    fake_credit_cards = set()

    while len(fake_credit_cards) < num_cc:
        fake_credit_cards.add(fake.credit_card_number(random.choice(circuits)))

    return fake_credit_cards


def fake_fc(num_fc):
    fake_fiscal_codes = set()

    while len(fake_fiscal_codes) < num_fc:
        fake_fiscal_codes.add(fake.ssn())

    return fake_fiscal_codes


def fc_cc_couples(num_fc, min_cc_per_fc, max_cc_per_fc):
    if min_cc_per_fc > max_cc_per_fc:
        print("Error: minimum credit cards per fiscal code greater than maximum credit cards per fiscal code")
        exit(1)

    fc_cc = {}

    fiscal_codes = fake_fc(num_fc)

    for fc in fiscal_codes:
        fc_cc[fc] = set()
        tmp_num_cc_per_fc = random.randint(min_cc_per_fc, max_cc_per_fc)
        fc_cc[fc] = fake_cc(tmp_num_cc_per_fc)

    return fc_cc


def is_iso8601(date_to_check):
    try:
        parser.parse(date_to_check)
        return True
    except ValueError:
        return False


def input_trx_name_formatter(sender_code, trx_datetime):
    return "{}.{}.{}.{}.001.{}".format(APPLICATION_PREFIX_FILE_NAME, sender_code, TRANSACTION_LOG_FIXED_SEGMENT,
                                       parser.parse(trx_datetime).strftime('%Y%m%d.%H%M%S'), TRANSACTION_FILE_EXTENSION)


def serialize(dataset, columns, destination_path):
    dataset_dataframe = pd.DataFrame(dataset, columns=columns)
    trx_file_path = os.path.join(destination_path, )

    os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

    with open(trx_file_path, "a") as f:
        f.write(dataset_dataframe.to_csv(index=False, header=False, sep=CSV_SEPARATOR))

def flatten(dataset):
    res=[]
    for i in dataset:
        for j in dataset[i]:
            res.append([i,j])
    return res

def flatten_values(dataset):
    res=[]
    for i in dataset:
        for j in dataset[i]:
            res.append(j)
    return res

class IDPayDataset:
    """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Service"""

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
        fc_cc = fc_cc_couples(self.args.num_fc, self.args.min_cc_per_fc, self.args.max_cc_per_fc)
        transactions = []
        correlation_ids = set()
        ids_trx_acq = set()

        if not is_iso8601(self.args.datetime):
            print(f'Error: {self.args.datetime} is not ISO8601')
            exit(1)

        for fc in fc_cc.keys():
            for i in range(self.args.trx_per_fc):
                curr_pan = random.choice(list(fc_cc[fc]))

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
                        curr_pan,  # hpan
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
                        sha256(f"{curr_pan}".encode()).hexdigest().upper()[:29]  # PAR
                    ]
                )

        # Serialization
        serialize(transactions, transaction_columns, os.path.join(self.args.out_dir, self.args.datetime, input_trx_name_formatter(self.args.sender_code, self.args.datetime)))
        serialize(fc_cc.keys(), fc_columns, os.path.join(self.args.out_dir, self.args.datetime, 'fc'))
        serialize(flatten(fc_cc), fc_cc_columns, os.path.join(self.args.out_dir, self.args.datetime, 'fc_pan'))
        serialize(flatten_values(fc_cc), pans_columns, os.path.join(self.args.out_dir, self.args.datetime, 'pan'))
