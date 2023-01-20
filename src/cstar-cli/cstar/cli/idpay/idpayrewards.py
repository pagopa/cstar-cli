import os.path
import random
from datetime import datetime
from hashlib import sha256

import pandas as pd
from .idpay_utilities import serialize

reward_columnds = [
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
        with open(self.args.payment_provisions_export, 'r') as input_file:
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

            # Insert desired duplicates
            duplicates = random.sample(rewards, round(self.args.perc_dupl * len(rewards)))
            for d in duplicates:
                rewards.append(d)

            serialize(rewards, reward_columnds, os.path.join('.', self.args.out_dir,
                                                             'rewards-dispositive-' + datetime.now().strftime(
                                                                 '%Y%m%dT%H%M%S') + '.csv'))
