import base64
import hashlib
import hmac
import random
import string
import uuid

import json
import pgpy
import warnings

from faker import Faker
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

ACTIONS = ["CREATE", "DELETE"]
IMPORT_OUTCOMES = ["OK", "KO"]
PAYMENT_CIRCUITS = ['visa', 'mastercard', 'maestro', 'amex']

KO_REASON_MESSAGES = ['Invalid contract identifier format', 'Contract does not exist']

CONTRACTS_FILE_EXTENSION = ".json"
ENCRYPTED_FILE_EXTENSION = "pgp"
EXPORT_PREFIX = 'PAGOPAPM_NPG_CONTRACTS_'
PAYMENT_METHOD_CARD = 'CARD'
FAKE_HMAC_KEY = '211267819F06608404372185CBB9780DA0E66FBBED5CD395FFD9EE168AAB229F'.encode('utf-8')
INVALID_CONTRACT_IDENTIFIER_CHARACTERS = string.punctuation

PAYMENT_REVERSAL_RATIO = 100
POS_PHYSICAL_ECOMMERCE_RATIO = 5
PERSON_NATURAL_LEGAL_RATIO = 3


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

        fake = Faker('it_IT')

        header = {
            'file_id': EXPORT_PREFIX + str(datetime.now().strftime('%Y%m%d%H%M%S')) + '_OUT',
            'processing_start_time': str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')),
            'processing_end_time': str((datetime.now() + timedelta(seconds=10)).strftime('%Y-%m-%dT%H%M%SZ')),
            'export_id': str(uuid.uuid4()),
            'import_file_id': 'PAGOPAPM_NPG_CONTRACTS_' + str(datetime.now().strftime('%Y%m%d%H%M%S')),
            'extraction_time': str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')),  # extraction time from source system
            'contract_quantity': self.args.contracts_qty,
            'file_sequence_number': '001'
        }

        finalfile = {
            "header": header,
        }

        contracts = []

        j = 0

        for i in range(self.args.contracts_qty):
            if i % self.args.ratio_delete_contract == 1:
                action = ACTIONS[1]

                if j % self.args.ratio_ko_delete_contract == 1:
                    import_outcome = IMPORT_OUTCOMES[1]
                    reason_message = random.choice(KO_REASON_MESSAGES)
                    original_contract_identifier = uuid.uuid4().hex
                    random_broken_char_position = random.randint(1, len(original_contract_identifier))
                    print(original_contract_identifier)
                    print(random_broken_char_position)
                    contracts.append(
                        {
                            "action": action,
                            "import_outcome": import_outcome,
                            "reason_message": reason_message,
                            "original_contract_identifier": original_contract_identifier[
                                                            :random_broken_char_position] + random.choice(
                                INVALID_CONTRACT_IDENTIFIER_CHARACTERS) + original_contract_identifier[
                                                                          random_broken_char_position:]
                        }
                    )

                else:
                    import_outcome = IMPORT_OUTCOMES[0]
                    original_contract_identifier = uuid.uuid4().hex

                    contracts.append(
                        {
                            "action": action,
                            "import_outcome": import_outcome,
                            "original_contract_identifier": original_contract_identifier
                        }
                    )

                j = j + 1

            else:
                action = ACTIONS[0]
                import_outcome = IMPORT_OUTCOMES[0]
                payment_method = PAYMENT_METHOD_CARD
                pan = fake.credit_card_number(random.choice(PAYMENT_CIRCUITS))
                method_attributes = {
                    "pan_tail": pan[-4:],
                    "expdate": fake.credit_card_expire(),
                    "card_id_4": base64.b64encode(
                        hmac.new(FAKE_HMAC_KEY, pan.encode('utf-8'), hashlib.sha256).digest()).hex(),
                    "card_payment_circuit": str.upper(random.choice(PAYMENT_CIRCUITS)),
                    "new_contract_identifier": uuid.uuid4().hex,
                    "original_contract_identifier": uuid.uuid4().hex,
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

        contracts_file_path = self.args.out_dir + "/WALLET.CONTRACTS." + datetime.today().strftime(
            '%Y%m%d.%H%M%S') + ".001" + CONTRACTS_FILE_EXTENSION

        with open(contracts_file_path, "w") as f:
            json.dump(finalfile, f, indent=4)

        if self.args.pgp:
            with open(self.args.key) as public_key:
                pgp_key = public_key.read()
            if pgp_key is None:
                print("PGP public key is None")
                exit(1)

            pgp_file(contracts_file_path, pgp_key)

        print(f"Done")


def pgp_file(file_path: str, pgp_key_data: str):
    key = pgpy.PGPKey.from_blob(pgp_key_data)
    with open(file_path, "rb") as f:
        message = pgpy.PGPMessage.new(f.read(), file=True)
    encrypted = key[0].encrypt(message, openpgp=True)
    output_path = f"{file_path}.{ENCRYPTED_FILE_EXTENSION}"
    with open(output_path, "wb") as f:
        f.write(bytes(encrypted))

    return output_path
