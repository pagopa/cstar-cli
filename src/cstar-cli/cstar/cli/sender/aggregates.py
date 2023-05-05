from hashlib import sha256
import time
import random
import uuid
import filecmp

import numpy as np
import pandas as pd
import os
from datetime import datetime

CSV_SEPARATOR = ";"

SECONDS_IN_DAY = 86400
MAX_DAYS_BACK = 3

TRANSACTION_FILE_EXTENSION = ".csv"
OUTPUT_EXPECTED_EXTENSION = ".expected"
# This string token is not valid for aggregates greater than the Batch Service threshold
BATCH_SERVICE_FIRST_CHUNK = ".01"

CSTAR_FILE_PREFIX_FILE_NAME = "CSTAR"
ADE_FILE_PREFIX_FILE_NAME = "ADE"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"

CHECKSUM_PREFIX = "#sha256sum:"

PAYMENT_REVERSAL_RATIO = 10
PERSON_NATURAL_LEGAL_RATIO = 3
PAR_RATIO = 7

CURRENCY_ISO4217 = "978"
PAYMENT_CIRCUITS = [f"{i:02}" for i in range(11)]

OFFSETS = [
    ".000Z",
    ".000+01:00",
    ".500+01:30"
]

BIN = "40236010"
MCC = "4900"
FISCAL_CODE = "RSSMRA80A01H501U"
VAT = "12345678903"

FISCAL_CODE_TO_FAKE_ABI = {
    "IE9813461A": "SUMUP",
    "LU30726739": "STPAY",
    "04949971008": "BPAY1",
    "BG175325806": "ICARD",
    "09771701001": "TPAY1",
    "97898850157": "AMAZN",
    "97898850157": "AMAZON",
    "DE182769455": "EURON",
    "NL858620285B01": "UBER1"
}

BANCOMAT_ACQUIRERS_SENDER_ID = [
    "02008",
    "01005",
    "03069",
    "04949971008",
]


class Aggregates:
    """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Service"""

    def __init__(self, args):
        self.args = args

    def diff(self):
        if not self.args.files:
            raise ValueError("--files is mandatory")
        if not len(self.args.files) == 2:
            raise ValueError("--files accepts only two files")

        sorted_first = sort_file(self.args.files[0])
        sorted_second = sort_file(self.args.files[1])

        result = filecmp.cmp(sorted_first, sorted_second)
        print(result)

    def trx_and_aggr(self):
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

            if i % PAYMENT_REVERSAL_RATIO == 0:
                operation_type = "01"
            else:
                operation_type = "00"

            # Set the accounting date from 0 to MAX_DAYS_BACK days back compared to transmission_date
            accounting_date = time.strftime('%Y-%m-%d', time.localtime(
                datetime.today().timestamp() - SECONDS_IN_DAY * random.randint(0, MAX_DAYS_BACK)))

            # Set random number of transactions
            num_trx = random.randint(1, self.args.avg_trx * 2)

            # Set random amount
            total_amount = num_trx * random.randint(2000, 500000)

            if self.args.sender == "COBAN":
                acquirer_id = random.choice(BANCOMAT_ACQUIRERS_SENDER_ID)
            elif self.args.sender == "STPAY":
                acquirer_id = "LU30726739"
            elif self.args.sender == "SUMUP":
                acquirer_id = "IE9813461A"
            elif self.args.sender == "BPAY1":
                acquirer_id = "04949971008"
            elif self.args.sender == "ICARD":
                acquirer_id = "BG175325806"
            elif self.args.sender == "TPAY1":
                acquirer_id = "09771701001"
            elif self.args.sender == "AMAZN":
                acquirer_id = "97898850157"
            elif self.args.sender == "AMAZON":
                acquirer_id = "97898850157"
            elif self.args.sender == "EURON":
                acquirer_id = "DE182769455"
            elif self.args.sender == "UBER1":
                acquirer_id = "NL858620285B01"
            else:
                acquirer_id = sender_code

            merchant_id = sha256(f"merchant{i}".encode()).hexdigest()
            terminal_id = sha256(f"terminal{i}".encode()).hexdigest()

            fiscal_code = str(i).zfill(11)

            if i % self.args.ratio_dirty_vat == 0:
                vat = "###na###"
                # Grants that at least 2 transactions are aggregated in case of dirty VAT
                num_trx = num_trx + 1
            else:
                vat = str(i).zfill(11)

            if i % self.args.ratio_dirty_pos_type == 0:
                pos_type = "99"
                # Grants that at least 2 transactions are aggregated in case of dirty pos_type
                num_trx = num_trx + 1
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
                    acquirer_id,
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

        now_timestamp = datetime.today().strftime('%Y%m%d.%H%M%S')

        aggr_df = pd.DataFrame(aggregates, columns=columns)

        aggr_file_path = self.args.out_dir + "/" + ADE_FILE_PREFIX_FILE_NAME + "." + str(
            sender_code) + "." + "TRNLOG" + "." + now_timestamp + ".001" + BATCH_SERVICE_FIRST_CHUNK \
                         + TRANSACTION_FILE_EXTENSION + OUTPUT_EXPECTED_EXTENSION

        os.makedirs(os.path.dirname(aggr_file_path), exist_ok=True)

        with open(aggr_file_path, "a") as f:
            f.write(aggr_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR, lineterminator='\n'))

        # GENERATE INPUT FILE

        transactions = []

        for aggr in aggregates:

            # Generate transactions with random amounts that sum up to the total amount
            n, k = aggr[5], aggr[4]
            amounts = np.random.default_rng().multinomial(n, [1 / k] * k, size=1)[0]

            for i in range(0, int(aggr[4])):

                operation_type = aggr[1]
                payment_circuit = random.choice(PAYMENT_CIRCUITS)

                date_time = time.strftime(aggr[3] + 'T%H:%M:%S' + random.choice(OFFSETS), time.localtime(
                    datetime.today().timestamp() - SECONDS_IN_DAY * random.random() * MAX_DAYS_BACK))

                id_trx_acquirer = uuid.uuid4().int
                id_trx_issuer = uuid.uuid4().int

                correlation_id = ""
                if aggr[1] == "01":
                    correlation_id = uuid.uuid4().int

                aggregate_acquirer_id = aggr[7]

                if aggregate_acquirer_id in FISCAL_CODE_TO_FAKE_ABI:
                    acquirer_id = FISCAL_CODE_TO_FAKE_ABI.get(aggregate_acquirer_id)
                else:
                    acquirer_id = aggregate_acquirer_id

                merchant_id = aggr[8]
                terminal_id = aggr[9]
                fiscal_code = aggr[10]

                vat = aggr[11]
                if vat == "###na###":
                    if i == 0:
                        vat = "12345678901"
                    else:
                        vat = VAT

                pos_type = aggr[12]
                if pos_type == "99" and i == 0:
                    pos_type = "01"
                else:
                    pos_type = "00"

                par = ''
                if i % PAR_RATIO == 0:
                    par = str(uuid.uuid4().int)[:29]

                transactions.append(
                    [
                        sender_code,
                        operation_type,
                        payment_circuit,
                        f"{self.args.pans_prefix + str(i)}",
                        date_time,
                        id_trx_acquirer,
                        id_trx_issuer,
                        correlation_id,
                        amounts[i],
                        CURRENCY_ISO4217,
                        acquirer_id,
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
        trx_file_path = self.args.out_dir + "/" + CSTAR_FILE_PREFIX_FILE_NAME + "." + str(sender_code) + "." \
                        + TRANSACTION_LOG_FIXED_SEGMENT + "." + now_timestamp + ".001" + TRANSACTION_FILE_EXTENSION

        os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

        with open(trx_file_path, "a") as f:
            csv_content = trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR, lineterminator="\n")
            f.write(CHECKSUM_PREFIX + sha256(
                f"{csv_content}".encode()).hexdigest() + "\n")
            f.write(csv_content)

        print(f"Done")


def sort_file(filename):
    infile = open(filename)
    words = []
    for line in infile:
        temp = line.split()
        for i in temp:
            words.append(i)
    infile.close()
    words.sort()
    outfile = open(filename, "w")
    for i in words:
        outfile.writelines(i)
        outfile.writelines("\n")
    outfile.close()
    return filename
