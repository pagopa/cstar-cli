from hashlib import sha256
import random
import uuid
import pandas as pd

CSV_SEPARATOR = ";"
PAN_UNENROLLED_PREFIX = "pan_unknown_"

PAYMENT_REVERSAL_RATIO = 30
POS_PHYSICAL_ECOMMERCE_RATIO = 5
PERSON_NATURAL_LEGAL_RATIO = 3
PAR_RATIO = 7

ACQUIRER_CODE = "99999"
CURRENCY_ISO4217 = "978"
PAYMENT_CIRCUITS = [f"{i:02}" for i in range(11)]
DATE_TIME = "2020-08-06T12:19:16.000+00:00"
ACQUIRER_ID = "09509"
MERCHANT_ID = "400000080205"
TERMINAL_ID = "80205005"
BIN = "40236010"
MCC = "4900"
FISCAL_CODE = "FC123456"
VAT = "12345678901"


class Transactionfilter:
    """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Acquirer"""

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
        """Produces a synthetic version of the CSV file produced by the acquirers

        Parameters:
          --pans-prefix: synthetic PANs will be generated as "{PREFIX}{NUMBER}"
          --pans-qty: the number of enrolled PANs to use in generated transactions
          --trx-qty: the number of transactions to generate in output
          --ratio: the ratio between transactions belonging to an enrolled PAN versus unenrolled (expressed as 1/ratio)
        """
        if not self.args.pans_prefix:
            raise ValueError("--pans-prefix is mandatory")
        if not self.args.pans_qty:
            raise ValueError("--pans-qty is mandatory")
        if not self.args.trx_qty:
            raise ValueError("--trx-qty is mandatory")
        if not self.args.ratio:
            raise ValueError("--ratio is mandatory")

        synthetic_pans_enrolled = [
            f"{self.args.pans_prefix}{i}" for i in range(self.args.pans_qty)
        ]
        synthetic_pans_not_enrolled = [
            f"{PAN_UNENROLLED_PREFIX}{i}" for i in range(self.args.pans_qty)
        ]

        transactions = []

        for i in range(self.args.trx_qty):

            operation_type = "00"
            if i % PAYMENT_REVERSAL_RATIO == 0:
                operation_type = "01"

            if i % self.args.ratio == 0:
                pan = random.choice(synthetic_pans_enrolled)
            else:
                pan = random.choice(synthetic_pans_not_enrolled)

            id_trx_acquirer = uuid.uuid4().int
            id_trx_issuer = uuid.uuid4().int
            payment_circuit = random.choice(PAYMENT_CIRCUITS)

            correlation_id = ""
            if operation_type == "01":
                correlation_id = uuid.uuid4().int

            total_amount = random.randint(1, 1000000)

            pos_type = "00"
            if i % POS_PHYSICAL_ECOMMERCE_RATIO == 0:
                pos_type = "01"

            vat = VAT
            if i % PERSON_NATURAL_LEGAL_RATIO == 0:
                vat = ""

            par = ""
            if i % PAR_RATIO == 0:
                par = str(uuid.uuid4())

            transactions.append(
                [
                    ACQUIRER_CODE,
                    operation_type,
                    payment_circuit,
                    pan,
                    DATE_TIME,
                    id_trx_acquirer,
                    id_trx_issuer,
                    correlation_id,
                    total_amount,
                    CURRENCY_ISO4217,
                    ACQUIRER_ID,
                    MERCHANT_ID,
                    TERMINAL_ID,
                    BIN,
                    MCC,
                    FISCAL_CODE,
                    vat,
                    pos_type,
                    par,
                ]
            )

        columns = [
            "acquirer_code",
            "operation_type",
            "circuit_type",
            "hpan",
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
        trx_df = pd.DataFrame(transactions, columns=columns)
        print(trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR))
