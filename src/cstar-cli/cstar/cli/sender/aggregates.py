from hashlib import sha256
import time
import random
import uuid

import numpy as np
import pandas as pd
import os
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

PAYMENT_REVERSAL_RATIO = 10
NO_VAT_RATIO = 50
NO_POS_TYPE_RATIO = 50
PERSON_NATURAL_LEGAL_RATIO = 3
PAR_RATIO = 7

CURRENCY_ISO4217 = "978"
PAYMENT_CIRCUITS = [f"{i:02}" for i in range(11)]

OFFSETS = [
    ".000Z",
    ".000+01:00",
    ".500+01:30"
]
SENDER_ID = "09509"
MERCHANT_ID = "400000080205"
TERMINAL_ID = "80205005"
BIN = "40236010"
MCC = "4900"
FISCAL_CODE = "RSSMRA80A01H501U"
VAT = "12345678903"


class Aggregates:
    """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Service"""

    def __init__(self, args):
        self.args = args

    def example_out(self):
        if not self.args.qty:
            raise ValueError("--qty is mandatory")

        # Set the sender code (common to all aggregates)
        sender_code = self.args.sender

        # Set the transmission date (common to all aggregates)
        transmission_date = datetime.today().strftime('%Y-%m-%d')

        aggregates = []

        for i in range(self.args.qty):

            if i % PAYMENT_REVERSAL_RATIO == 0:
                operation_type = "01"
            else:
                operation_type = "00"

            # Set the accounting date from 0 to MAX_DAYS_BACK days back compared to transmission_date
            accounting_date = time.strftime('%Y-%m-%d', time.localtime(
                datetime.today().timestamp() - SECONDS_IN_DAY * random.randint(0, MAX_DAYS_BACK)))

            # Set random number of transactions
            num_trx = random.randint(1, 20)

            # Set random amount
            total_amount = num_trx * random.randint(2000, 500000)

            merchant_id = abs(hash(sha256(f"merchant{i}".encode()).hexdigest()))
            terminal_id = abs(hash(sha256(f"terminal{i}".encode()).hexdigest()))

            fiscal_code = str(i).zfill(11)

            if i % NO_VAT_RATIO == 0:
                vat = ""
            else:
                vat = str(i).zfill(11)

            if i % NO_POS_TYPE_RATIO == 0:
                # pos_type = "127"
                pos_type = "00"
            else:
                pos_type = "00"

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

        aggr_df = pd.DataFrame(aggregates, columns=columns)
        aggr_file_path = self.args.out_dir + "/" + APPLICATION_PREFIX_FILE_NAME + "." + str(
            sender_code) + "." + "OUTEXAMPLE" + "." + datetime.today().strftime(
            '%Y%m%d.%H%M%S') + ".001" + TRANSACTION_FILE_EXTENSION

        os.makedirs(os.path.dirname(aggr_file_path), exist_ok=True)

        with open(aggr_file_path, "a") as f:
            f.write(aggr_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR))

        # GENERATE INPUT FILE

        transactions = []

        for aggr in aggregates:

            # Generate transactions with random amounts that sum up to the total amount
            n, k = aggr[5], aggr[4]
            amounts = np.random.default_rng().multinomial(n, [1 / k] * k, size=1)[0]

            for i in range(0, int(aggr[4])):

                operation_type = aggr[1];
                payment_circuit = random.choice(PAYMENT_CIRCUITS)

                date_time = time.strftime(aggr[3] + 'T%H:%M:%S' + random.choice(OFFSETS), time.localtime(
                    datetime.today().timestamp() - SECONDS_IN_DAY * random.random() * MAX_DAYS_BACK))

                id_trx_acquirer = uuid.uuid4().int
                id_trx_issuer = uuid.uuid4().int

                correlation_id = ""
                if aggr[1] == "01":
                    correlation_id = uuid.uuid4().int

                merchant_id = aggr[8];
                terminal_id = aggr[9];
                fiscal_code = aggr[10];

                vat = aggr[11];
                pos_type = aggr[12];

                par = ''
                if i % PAR_RATIO == 0:
                    par = str(uuid.uuid4())

                transactions.append(
                    [
                        sender_code,
                        operation_type,
                        payment_circuit,
                        f"{'pan' + str(i)}",
                        date_time,
                        id_trx_acquirer,
                        id_trx_issuer,
                        correlation_id,
                        amounts[i],
                        CURRENCY_ISO4217,
                        sender_code,
                        merchant_id,
                        terminal_id,
                        BIN,
                        MCC,
                        fiscal_code,
                        vat,
                        pos_type,
                        par
                    ]
                )

        columns = [
            "acquirer_code",
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

        if self.args.shuffle:
            random.shuffle(transactions)

        trx_df = pd.DataFrame(transactions, columns=columns)
        trx_file_path = self.args.out_dir + "/" + APPLICATION_PREFIX_FILE_NAME + "." + str(
            sender_code) + "." + TRANSACTION_LOG_FIXED_SEGMENT + "." + datetime.today().strftime(
            '%Y%m%d.%H%M%S') + ".001" + TRANSACTION_FILE_EXTENSION

        os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

        with open(trx_file_path, "a") as f:
            f.write(trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR))

        with open(aggr_file_path, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(CHECKSUM_PREFIX + sha256(
                f"{trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR)}".encode()).hexdigest().rstrip(
                '\r\n') + '\n' + content)

    print(f"Done")
