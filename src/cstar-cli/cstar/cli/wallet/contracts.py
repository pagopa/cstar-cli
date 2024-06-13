import base64
import hashlib
import hmac
import os
import random
import time
import string
import sys
import uuid

import json
import pgpy
import warnings

import requests
from faker import Faker
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

ACTIONS = ["CREATE", "DELETE"]
IMPORT_OUTCOMES = ["OK", "KO"]
PAYMENT_CIRCUITS = ['visa', 'mastercard', 'maestro', 'amex', 'diners']
PAYMENT_CIRCUITS_SHORT = ['visa', 'mc', 'maestro', 'amex', 'diners']

KO_REASON_MESSAGES = ['Invalid contract identifier format', 'Contract does not exist']

DECRYPTED_FILE_EXTENSION = ".decrypted"
HMAC_FILE_EXTENSION = ".hmac"
EXPORT_PREFIX = 'PAGOPAPM_NPG_CONTRACTS_'
EXPORT_SUFFIX = '_001_OUT'
PAYMENT_METHOD_CARD = 'CARD'
FAKE_HMAC_KEY = '211267819F06608404372185CBB9780DA0E66FBBED5CD395FFD9EE168AAB229F'.encode('utf-8')
INVALID_CONTRACT_IDENTIFIER_CHARACTERS = string.punctuation

PAYMENT_REVERSAL_RATIO = 100
POS_PHYSICAL_ECOMMERCE_RATIO = 5
PERSON_NATURAL_LEGAL_RATIO = 3

fake = Faker('it_IT')


class Contracts:
    """Utilities related to the migration of Payment Manager wallets"""

    def __init__(self, args):
        self.args = args

    def fake_wallet_migration(self):
        """Produces wallets for testing purposes

        Parameters:
          --wallets-qty: the number of contracts to generate in output
          --ratio-delete: the ratio between CREATE and DELETE action (expressed as 1/ratio) ( default = 1 )
          --ratio-ko: the ratio between OK and KO import_outcome (expressed as 1/ratio) ( default = 1 )
        """

        file_id = EXPORT_PREFIX + str(datetime.now().strftime('%Y%m%d%H%M%S')) + EXPORT_SUFFIX

        header = {
            'file_id': file_id,
            'tenant_id': str(uuid.uuid4()),
            'merchant_id': str(uuid.uuid4()),
            'terminal_id': str(uuid.uuid4()),
            'processing_start_time': str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')),
            'processing_end_time': str((datetime.now() + timedelta(seconds=10)).strftime('%Y-%m-%dT%H%M%SZ')),
            'export_id': str(uuid.uuid4()),
            'import_file_id': str(random.randint(1, 99999)),
            'extraction_time': str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')),  # extraction time from source system
            'contract_quantity': str(self.args.contracts_qty),
            'file_sequence_number': '001'
        }

        finalfile = {
            "header": header,
        }

        contracts = []
        contract_ids = []

        j = 0

        for i in range(self.args.contracts_qty):

            if self.args.true_ids:
                if self.args.wallet_api_key is None:
                    sys.exit(f"No valid Wallet API key provided")
                else:
                    contract_identifier = real_contract_id(self.args.env, self.args.wallet_api_key)
            else:
                contract_identifier = uuid.uuid4().hex

            contract_ids.append(contract_identifier)

            if self.args.ratio_delete_contract and i % self.args.ratio_delete_contract == 1:
                action = ACTIONS[1]

                if self.args.ratio_ko_delete_contract and j % self.args.ratio_ko_delete_contract == 1:
                    import_outcome = IMPORT_OUTCOMES[1]
                    reason_message = random.choice(KO_REASON_MESSAGES)
                    random_broken_char_position = random.randint(1, len(contract_identifier))

                    contracts.append(
                        {
                            "action": action,
                            "import_outcome": import_outcome,
                            "reason_message": reason_message,
                            "original_contract_identifier": contract_identifier[
                                                            :random_broken_char_position] + random.choice(
                                INVALID_CONTRACT_IDENTIFIER_CHARACTERS) + contract_identifier[
                                                                          random_broken_char_position:]
                        }
                    )

                else:
                    import_outcome = IMPORT_OUTCOMES[0]

                    contracts.append(
                        {
                            "action": action,
                            "import_outcome": import_outcome,
                            "original_contract_identifier": contract_identifier
                        }
                    )

                j = j + 1

            else:
                action = ACTIONS[0]
                import_outcome = IMPORT_OUTCOMES[0]
                payment_method = PAYMENT_METHOD_CARD
                current_payment_circuit = random.randint(0, len(PAYMENT_CIRCUITS) - 1)
                pan = fake.credit_card_number(PAYMENT_CIRCUITS[current_payment_circuit])
                method_attributes = {
                    "pan_tail": pan[-4:],
                    "expdate": fake.credit_card_expire(),
                    "card_id_4": base64.b64encode(
                        hmac.new(FAKE_HMAC_KEY, pan.encode('utf-8'), hashlib.sha256).digest()).hex(),
                    "card_payment_circuit": str.upper(PAYMENT_CIRCUITS_SHORT[current_payment_circuit]),
                    "new_contract_identifier": contract_identifier,
                    "original_contract_identifier": contract_identifier,
                    "card_bin": pan[:6]
                }

                contracts.append(
                    {
                        "action": action,
                        "import_outcome": import_outcome,
                        "payment_method": payment_method,
                        "method_attributes": method_attributes
                    }
                )

        finalfile['contracts'] = contracts

        contracts_file_path = os.path.join(self.args.out_dir, file_id)
        decrypted_contracts_file_path = contracts_file_path + DECRYPTED_FILE_EXTENSION

        with open(decrypted_contracts_file_path, "w") as f:
            json.dump(finalfile, f, indent=4)

        if self.args.pgp:
            with open(self.args.key) as public_key:
                pgp_key = public_key.read()
            if pgp_key is None:
                print("PGP public key is None")
                exit(1)

            pgp_file(decrypted_contracts_file_path, contracts_file_path, pgp_key)

        if self.args.hmac_key:
            hmac_file(contract_ids, contracts_file_path, self.args.hmac_key)

        print(f"Done")


def real_contract_id(env: str, wallet_api_key: str) -> str:
    i = 0
    tries = 5
    fake_fc = fake.ssn()
    fake_fc = f'{fake_fc[:11]}X000{fake_fc[15:]}'
    while i < tries:
        res = requests.put(
            url=f'https://api.{env}.platform.pagopa.it/payment-wallet-migrations/v1/migrations/wallets',
            headers={
                'Ocp-Apim-Subscription-Key': wallet_api_key
            },
            json={
                "walletIdPm": random.randint(0, 99999999),
                "fiscalCode": fake_fc
            },
            timeout=60000
        )
        if res.status_code == 429:
            time.sleep(int(res.headers["Retry-After"]) / 1000)
            i += 1
        elif res.status_code != 200:
            sys.exit(f"Failed to get contract id from wallet. Status code {res.status_code}", )
        else:
            return res.json()['contractId']


def pgp_file(decrypted_file_path: str, encrypted_file_path: str, pgp_key_data: str):
    key = pgpy.PGPKey.from_blob(pgp_key_data)
    with open(decrypted_file_path, "rb") as f:
        message = pgpy.PGPMessage.new(f.read(), file=True)
    encrypted = key[0].encrypt(message, openpgp=True)
    with open(encrypted_file_path, "wb") as f:
        f.write(bytes(encrypted))

    return encrypted_file_path


def hmac_file(contract_ids: [], encrypted_file_path: str, hmac_key_base64: str):
    hmac_file_path = encrypted_file_path + HMAC_FILE_EXTENSION
    hmac_key_bytes = base64.b64decode(hmac_key_base64)

    hmacs = []

    for contract_id in contract_ids:
        hmacs.append(hmac.HMAC(key=hmac_key_bytes, msg=contract_id.encode('utf-8'),
                               digestmod=hashlib.sha256).digest().hex())

    with open(hmac_file_path, "w") as f:
        json.dump(hmacs, f, indent=4)
