from hashlib import sha256
import time
import random
import uuid
import pandas as pd
import os
import json
import pgpy
import warnings

from faker import Faker
from datetime import datetime

warnings.filterwarnings("ignore")

CSV_SEPARATOR = ";"
PAN_UNENROLLED_PREFIX = "pan_unknown_"

SECONDS_IN_DAY = 86400
MAX_DAYS_BACK = 3

TRANSACTION_FILE_EXTENSION = ".csv"
ENCRYPTED_FILE_EXTENSION = "pgp"
APPLICATION_PREFIX_FILE_NAME = "CSTAR"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"
CHECKSUM_PREFIX = "#sha256sum:"

CARDS_FILE_EXTENSION = ".json"
CARDS_FILE_PREFIX_ENROLL = "ENROLL"
CARDS_FILE_PREFIX_TKM = "TKM"
CARDS_FILE_HPANS_NAME = "CARDS_SYNTHETIC_PANS"
CARDS_FILE_SYNTHETICS_PAN_NAME = "CARDS_HASHPANS"
CARDS_FILE_HASPANS_PAN_EXTENSION = ".txt"

PAYMENT_REVERSAL_RATIO = 100
POS_PHYSICAL_ECOMMERCE_RATIO = 5
PERSON_NATURAL_LEGAL_RATIO = 3

CURRENCY_ISO4217 = "978"
PAYMENT_CIRCUITS = [f"{i:02}" for i in range(11)]

OFFSETS = [
    ".000Z",
    ".000+01:00",
    ".500+01:30"
]

MERCHANT_ID = "400000080205"
TERMINAL_ID = "80205005"
BIN = "40236010"

FISCAL_CODE = "RSSMRA80A01H501U"
VAT = "12345678903"

PAR_YES = "YES"
PAR_NO = "NO"
PAR_RANDOM = "RANDOM"

STATE_ALL = "ALL"
STATE_REVOKED = "REVOKED"


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
          --pans-prefix: synthetic PANs will be generated as "{PREFIX}{NUMBER}" ( default = "prefix_" )
          --pans-qty: the number of enrolled PANs to use in generated transactions ( default = 10 )
          --trx-qty: the number of transactions to generate in output
          --ratio: the ratio between transactions belonging to an enrolled PAN versus unenrolled (expressed as 1/ratio) ( default = 1 )
          --pos-number: how many different synthetic POS must be created
          --mcc:  Merchant Category Code ( default = 6010 )
          --input-file: pan or hashpan to use in transaction generation
          --par-ratio: a ratio to have transaction with par every # transaction ( default = 1 )
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
        if len(self.args.sender) is not 5:
            raise ValueError("--sender must be of length 5")

        input_file = self.args.input_hashpans
        fake = Faker('it_IT')

        # Set the sender code (common to all transactions)
        sender_code = self.args.sender

        if input_file == "":
            synthetic_pans_enrolled = [
                f"{self.args.pans_prefix}{i}" for i in range(self.args.pans_qty)
            ]
            synthetic_pans_not_enrolled = [
                f"{PAN_UNENROLLED_PREFIX}{i}" for i in range(self.args.pans_qty)
            ]
        else:
            with open(input_file, 'r') as input_pans:
                synthetic_pans_enrolled = input_pans.read().splitlines()
                if len(synthetic_pans_enrolled) == 0:
                    print("The hashpan file must not be empty")
                    exit(1)
                synthetic_pans_not_enrolled = []

        synthetic_pos = []
        for i in range(self.args.pos_number):
            synthetic_pos.append([
                str(1000000 + i),  # terminal_id
                str(2000000 + i),  # merchant_id,
                fake.ssn(),  # fiscal_code
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

            if input_file == "":
                if i % self.args.ratio == 0:
                    pan = random.choice(synthetic_pans_enrolled)
                else:
                    pan = random.choice(synthetic_pans_not_enrolled)
            else:
                pan = random.choice(synthetic_pans_enrolled)

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
            if i % self.args.par_ratio == 0:
                par = sha256(f"{pan}".encode()).hexdigest().upper()[:29]

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
                    self.args.mcc,
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
            "pan",
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
            csv_content = trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR, lineterminator="\n")
            f.write(CHECKSUM_PREFIX + sha256(
                f"{csv_content}".encode()).hexdigest() + "\n")
            f.write(csv_content)

        if self.args.pgp:
            # Encryption of transaction file
            with open(self.args.key) as public_key:
                pgp_key = public_key.read()
            if pgp_key is None:
                print("PGP public key is None")
                exit(1)

            pgp_file(trx_file_path, pgp_key)

        print(f"Done")

    def synthetic_cards(self):
        """Produces a synthetic cards data for enrolled payment instrument microservice

        Parameters:
          --pans-prefix: synthetic PANs will be generated as "{PREFIX}{NUMBER}"
          --crd-qty: the number of cards to generate in output
          --max-num-children: the max number of hashpans card children for each card
          --num-children: the precise number of hashpans card children for each card
          --par: par flag (YES | NO | RANDOM ->  defult:RANDOM)
          --state: state of the cards (READY | ALL -> default:ALL)
          --salt: the salt to use when performing PAN hashing
          --revoked-percentage: number between 0 and 100 for the percentage of revoked cards (default=10%)
        """

        if not self.args.pans_prefix:
            raise ValueError("--pans-prefix is mandatory")
        if not self.args.crd_qty:
            raise ValueError("--crd-qty is mandatory")
        if self.args.max_num_children and self.args.num_children:
            raise ValueError("you can set only one value between --max-num-children and --num-children")
        if not self.args.salt:
            raise ValueError("--salt is mandatory")

        synthetic_pans = []
        hpans = []

        output_list_enroll = []
        output_list_tkm = []

        for i in range(0, self.args.crd_qty):
            temp_hashpanexports = []
            temp_hashtokens = []
            card_children = 0
            temp_par = ""

            synthetic_pan = f"{self.args.pans_prefix}{i}"
            hpan_f = sha256(f"{self.args.pans_prefix}{i}{self.args.salt}".encode()).hexdigest()
            synthetic_pans.append(synthetic_pan)
            hpans.append(hpan_f)
            temp_hashpanexports.append({"value": hpan_f})

            enroll_var = {
                "hpanList": [
                    {"hpan": hpan_f, "consent": True}
                ],
                "operationType": "ADD_INSTRUMENT",
                "application": "ID_PAY"
            }

            tkm_var = {
                "taxCode": "",
            }

            if self.args.par == PAR_YES:
                temp_par = sha256(f"{synthetic_pan}".encode()).hexdigest().upper()[:29]
            elif self.args.par == PAR_RANDOM and random.randint(0, 1) == 1:
                temp_par = sha256(f"{synthetic_pan}".encode()).hexdigest().upper()[:29]

            if self.args.max_num_children:
                card_children = random.randint(0, self.args.max_num_children)
            elif self.args.num_children:
                card_children = self.args.num_children

            if len(temp_par) != 0:
                for child in range(0, card_children):
                    synthetic_pan = f"{self.args.pans_prefix}{i}_{child}"
                    hpan_c = sha256(f"{self.args.pans_prefix}{i}_{child}{self.args.salt}".encode()).hexdigest()
                    synthetic_pans.append(synthetic_pan)
                    hpans.append(hpan_c)
                    temp_htoken = {
                        "htoken": hpan_c,
                        "haction": "INSERT_UPDATE"
                    }
                    temp_hashtokens.append(temp_htoken)

                tkm_var["timestamp"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

                tkm_var["cards"] = [{
                    "hpan": hpan_f,
                    "par": temp_par,
                    "action": "INSERT_UPDATE",
                    "htokens": temp_hashtokens
                }]
                output_list_tkm.append(tkm_var)

            if self.args.state == "ALL" and random.random() <= (self.args.revoked_percentage * 0.01):
                revoked_tkm_ev = {
                    "taxCode": "",
                    "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "cards": [{
                        "hpan": hpan_f,
                        "action": STATE_REVOKED,
                        "htokens": []
                    }
                    ]
                }
                output_list_tkm.append(revoked_tkm_ev)

            output_list_enroll.append(enroll_var)

        enroll_file_path = self.args.out_dir + "/" + CARDS_FILE_PREFIX_ENROLL + "_" + datetime.today().strftime(
            '%Y%m%d_%H%M%S') + CARDS_FILE_EXTENSION

        os.makedirs(os.path.dirname(enroll_file_path), exist_ok=True)

        with open(enroll_file_path, "a") as outfile:
            for en_card in output_list_enroll:
                enroll_json_output = json.dumps(en_card)
                outfile.write(enroll_json_output + "\n")

        tkm_file_path = self.args.out_dir + "/" + CARDS_FILE_PREFIX_TKM + "_" + datetime.today().strftime(
            '%Y%m%d_%H%M%S') + CARDS_FILE_EXTENSION

        os.makedirs(os.path.dirname(tkm_file_path), exist_ok=True)

        with open(tkm_file_path, "a") as outfile:
            for tkm_update in output_list_tkm:
                tkm_json_output = json.dumps(tkm_update)
                outfile.write(tkm_json_output + "\n")

        hashpans_file_path = self.args.out_dir + "/" + CARDS_FILE_HPANS_NAME + "_" + datetime.today().strftime(
            '%Y%m%d_%H%M%S') + CARDS_FILE_HASPANS_PAN_EXTENSION

        with open(hashpans_file_path, "a") as output_hashpans_file:
            for hpan in hpans:
                output_hashpans_file.write(hpan + "\n")

        synthetic_pans_file_path = self.args.out_dir + "/" + CARDS_FILE_SYNTHETICS_PAN_NAME + "_" + datetime.today().strftime(
            '%Y%m%d_%H%M%S') + CARDS_FILE_HASPANS_PAN_EXTENSION

        with open(synthetic_pans_file_path, "a") as output_pans_file:
            for pan in synthetic_pans:
                output_pans_file.write(pan + "\n")

        print(
            f"Enroll file {enroll_file_path}, tkm file {tkm_file_path}, hashpans {hashpans_file_path} and synthetic pans {synthetic_pans_file_path} were genereted")


def pgp_file(file_path: str, pgp_key_data: str):
    key = pgpy.PGPKey.from_blob(pgp_key_data)
    with open(file_path, "rb") as f:
        message = pgpy.PGPMessage.new(f.read(), file=True)
    encrypted = key[0].encrypt(message, openpgp=True)
    output_path = f"{file_path}.{ENCRYPTED_FILE_EXTENSION}"
    with open(output_path, "wb") as f:
        f.write(bytes(encrypted))

    return output_path
