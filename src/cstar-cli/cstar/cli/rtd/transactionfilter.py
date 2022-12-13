from hashlib import sha256
import time
import random
import uuid
import pandas as pd
import logging
import os
import gnupg
import json
from tempfile import TemporaryDirectory
from datetime import datetime,timedelta
from enum import Enum

CSV_SEPARATOR = ";"
PAN_UNENROLLED_PREFIX = "pan_unknown_"

SECONDS_IN_DAY = 86400
MAX_DAYS_BACK = 3

TRANSACTION_FILE_EXTENSION = ".csv"
ENCRYPTED_FILE_EXTENSION = ".pgp"
APPLICATION_PREFIX_FILE_NAME = "CSTAR"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"
CHECKSUM_PREFIX = "#sha256sum:"
CARDS_FILE_EXTENSION = ".json"

PAYMENT_REVERSAL_RATIO = 100
POS_PHYSICAL_ECOMMERCE_RATIO = 5
PERSON_NATURAL_LEGAL_RATIO = 3
PAR_RATIO = 7

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
MCC = "6010"
FISCAL_CODE = "RSSMRA80A01H501U"
VAT = "12345678903"

PAR_YES = "YES"
PAR_NO = "NO"
PAR_RANDOM = "RANDOM"

class CardState(Enum):
    READY = 0
    NOT_ENROLLED = 1
    REVOKED = 2
    ALL = 3


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
        if len(self.args.sender) is not 5:
            raise ValueError("--sender must be of length 5")

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
                "CF" + str(300000000 + i)[:9],  # fiscal_code
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
                pan = random.choice(synthetic_pans_enrolled)
            else:
                pan = random.choice(synthetic_pans_not_enrolled)

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
            f.write(CHECKSUM_PREFIX + sha256(
                f"{trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR)}".encode()).hexdigest() + "\n")
            f.write(trx_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR))

        if self.args.pgp:
            encrypt_file(trx_file_path, self.args.key)

        print(f"Done")


    
    def synthetic_cards(self):
        """Produces a synthetic cards data for enrolled payment instrument microservice

        Parameters:
          --pans-prefix: synthetic PANs will be generated as "{PREFIX}{NUMBER}"
          --crd-qty: the number of cards to generate in output
          --max-num-children: the max number of hashpans card children for each card
          --num-children: the precise number of hashpans card children for each card
          --par: par flag (YES | NO | RANDOM ->  defult:RANDOM)
          --state: state of the cards (READY | NOT_ENROLED | REVOKED | ALL -> default:ALL)
          --salt: the salt to use when performing PAN hashing
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
        db_card_struct_list = []

        for i in range(0,self.args.crd_qty):
            db_card_struct = {}
            temp_hashpanexports = []
            card_children = 0
            
            synthetic_pan = f"{self.args.pans_prefix}{i}"
            hpan_f = sha256(f"{self.args.pans_prefix}{i}{self.args.salt}".encode()).hexdigest()
            db_card_struct["hashPan"]= hpan_f
            synthetic_pans.append(synthetic_pan)
            hpans.append(hpan_f)
            temp_hashpanexports.append({"value":hpan_f})

            db_card_struct["hashPanChildren"] = []
            if self.args.max_num_children :
                card_children = random.randint(0,self.args.max_num_children)
            elif self.args.num_children:
                card_children = self.args.num_children
            
            for child in range(0,card_children):
                synthetic_pan = f"{self.args.pans_prefix}{i}_{child}"
                hpan_c = sha256(f"{self.args.pans_prefix}{i}_{child}{self.args.salt}".encode()).hexdigest()
                synthetic_pans.append(synthetic_pan)
                hpans.append(hpan_c
                db_card_struct["hashPanChildren"].append(hpan_c)
                temp_hashpanexports.append({"value":hpan_c})

            if self.args.par == PAR_YES:
                db_card_struct["par"] = sha256(f"{synthetic_pan}".encode()).hexdigest().upper()[:29]
            elif self.args.par == PAR_NO:
                db_card_struct["par"] = ""
            elif self.args.par == PAR_RANDOM and random.randint(0,1) == 1:
                db_card_struct["par"] = sha256(f"{synthetic_pan}".encode()).hexdigest().upper()[:29]
            
            db_card_struct["enabledApps"] = []
            if self.args.state == CardState.READY.name:
                db_card_struct["state"] = CardState.READY.name
                db_card_struct["enabledApps"].append("FA")
            elif self.args.state == CardState.NOT_ENROLLED.name:
                db_card_struct["state"] = CardState.NOT_ENROLLED.name
            elif self.args.state == CardState.REVOKED.name:
                db_card_struct["state"] = CardState.REVOKED.name
            elif self.args.state == CardState.ALL.name:
                db_card_struct["state"]=CardState(random.randint(0,2)).name
                if db_card_struct["state"] == CardState.READY.name:
                    db_card_struct["enabledApps"].append("FA")

            db_card_struct["hashPanExports"] = temp_hashpanexports
            db_card_struct["issuer"] = ""
            db_card_struct["network"] = ""
            now = datetime.now()
            unix_now =  time.mktime(now.timetuple())
            one_week_ago = now - timedelta(days=7)
            unix_one_week = time.mktime(one_week_ago.timetuple())
            db_card_struct["insertAt"] ={"$date": unix_one_week}
            if random.randint(0,1) == 1:
                db_card_struct["updatedAt"] = {"$date":unix_now}
            db_card_struct["version"] = self.args.version
            db_card_struct["insertUser"] = "enrolled_payment_instrument"
            db_card_struct["updateUser"] = "enrolled_payment_instrument"
            db_card_struct["_class"] = "it.gov.pagopa.rtd.ms.enrolledpaymentinstrument.infrastructure.persistence.mongo.EnrolledPaymentInstrumentEntity"

            db_card_struct_list.append(db_card_struct)
            
        json_output = json.dumps(db_card_struct_list,indent=10)

        crd_file_path = self.args.out_dir + "/" + "CARDS_" + datetime.today().strftime(
            '%Y%m%d.%H%M%S') + CARDS_FILE_EXTENSION

        os.makedirs(os.path.dirname(crd_file_path), exist_ok=True)


        with open(crd_file_path,"a") as outfile:
            outfile.write(json_output)

        print(f"A JSON file {crd_file_path} was genereted ")


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
