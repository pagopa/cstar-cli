import gzip
import uuid
from hashlib import sha256
import random

import pandas as pd
import os
from datetime import datetime

CSV_SEPARATOR = ";"

APPLICATION_PREFIX_FILE_NAME = "CSTAR"
ADE_ACK_FIXED_SEGMENT = "ADEACK"
RESULTS_FILE_EXTENSION = ".csv"
ZIPPED_FILE_EXTENSION = ".gzip"

SCARTI = [
    ['0101',
     '0104',
     '0105'],

    ['0204',
     '0205'],

    ['0304',
     '0305'],

    ['0403'
     '0404',
     '0405'],

    ['0502',
     '0504',
     '0505'],

    ['0604',
     '0605'],

    ['0704',
     '0705'],

    ['0804',
     '0805'],

    ['0904',
     '0905'],

    ['1004',
     '1005'],

    ['1104',
     '1105'],

    ['1204',
     '1205',
     '1206'],

    ['1304'],

    ['1404',
     '1405']
]

SEGNALAZIONI = [
    ['1201',
     '1204'],

    ['1302',
     '1303',
     '1304'],

]


class Results:
    """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Acquirer"""

    def __init__(self, args):
        self.args = args

    def synthetic_results(self):
        """Produces a synthetic version of the CSV file produced by the acquirers for RTD

        Parameters:
            --res-qty: the number of results generated
            -o, --out-dir: path to the directory where the file will be created, default is "."
            --gzip: if set, also a gzipped version of the file is created
        """

        if not self.args.res_qty:
            raise ValueError("--res-qty is mandatory")

        results = []

        for i in range(self.args.res_qty):

            lista_errori = ''

            esito = random.randint(0, 4)
            match esito:
                case 1:
                    lista_errori = "1206"
                case 3:
                    lista_errori = "1201"
                case 2:
                    for bad_field in random.sample(SCARTI, random.randint(1, 14)):
                        lista_errori = lista_errori + random.choice(bad_field) + '|'
                    print(lista_errori)
                    lista_errori = lista_errori.removesuffix("|")
                    print(lista_errori)
                case 4:
                    for bad_field in random.sample(SEGNALAZIONI, random.randint(1, 2)):
                        lista_errori = lista_errori + random.choice(bad_field) + '|'
                    print(lista_errori)
                    lista_errori = lista_errori.removesuffix("|")
                    print(lista_errori)

            results.append(
                [
                    str(uuid.uuid4()),
                    esito,
                    lista_errori
                ])

        columns = [
            "record_id",
            "esito",
            "lista_errori"
        ]
        results_df = pd.DataFrame(results, columns=columns)
        results_df_path = self.args.out_dir + "/" + APPLICATION_PREFIX_FILE_NAME + "." + ADE_ACK_FIXED_SEGMENT + "." + datetime.today().strftime(
            '%Y%m%d.%H%M%S') + ".001" + RESULTS_FILE_EXTENSION

        os.makedirs(os.path.dirname(results_df_path), exist_ok=True)

        with open(results_df_path, "a") as f:
            f.write(results_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR))

        if self.args.gzip:
            with gzip.open(results_df_path + ZIPPED_FILE_EXTENSION, "wb") as f:
                f.write(bytes(results_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR), encoding='utf-8'))

        print("Done")
