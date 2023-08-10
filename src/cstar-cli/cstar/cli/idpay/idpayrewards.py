import os.path
import random
import zipfile
from datetime import datetime
from hashlib import sha256

import pandas as pd
from .idpay_utilities import serialize

reward_columns = [
    'uniqueID',
    'result',
    'rejectionReason',
    'cro',
    'executionDate'
]
possible_results = [
    'OK - ORDINE ESEGUITO',
    'KO'
]
possible_rejectReasons = [
    'IBAN NOT VALID'
]


class IDPayRewards:
    def __init__(self, args):
        self.args = args

    def rewards(self):
        new_input_file_name = self.args.payment_provisions_export
        if self.args.payment_provisions_export.endswith('.zip'):
            with zipfile.ZipFile(self.args.payment_provisions_export) as ziped_input_file:
                new_input_file_name = self.args.payment_provisions_export.replace('.zip', '.csv')
                ziped_input_file.extract(os.path.basename(new_input_file_name))
        with open(new_input_file_name, 'r') as input_file:
            input_file.seek(0)
            payments = pd.read_csv(input_file, quotechar='"', usecols=['uniqueID'], sep=';')

            execution_date = self.args.exec_date
            if self.args.exec_date is None:
                execution_date = datetime.now().strftime('%Y-%m-%d')

            rewards = []
            i = 0
            for payment in payments.values:
                curr_cro = sha256(f"{i}".encode()).hexdigest()
                i = i + 1
                curr_execution_date = execution_date
                # Decide whether the reward is OK or KO based on desired probability
                if random.random() < self.args.perc_succ:
                    curr_result = possible_results[0]
                    curr_reject_reason = ''
                else:
                    curr_result = possible_results[1]
                    curr_reject_reason = possible_rejectReasons[0]
                    curr_cro = ''
                    curr_execution_date = ''

                rewards.append([
                    payment[0],
                    curr_result,
                    curr_reject_reason,
                    curr_cro,
                    curr_execution_date
                ])

            output_file_name = 'rewards-dispositive-' + datetime.now().strftime('%Y%m%dT%H%M%S')
            ourput_file_path = os.path.join('.', self.args.out_dir, output_file_name)

            # Insert desired duplicates
            duplicates = random.sample(rewards, round(self.args.perc_dupl * len(rewards)))
            for d in duplicates:
                rewards.append(d)

            serialize(rewards, reward_columns, ourput_file_path + '.csv', True)

            with zipfile.ZipFile(ourput_file_path + '.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                zf.write(ourput_file_path + '.csv', arcname=output_file_name + '.csv')
