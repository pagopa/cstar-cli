from hashlib import sha256

import pandas as pd
import os
from datetime import datetime

CSV_SEPARATOR = ";"

APPLICATION_PREFIX_FILE_NAME = "CSTAR"
ADE_ACK_FIXED_SEGMENT = "ADEACK"
RESULTS_FILE_EXTENSION = ".csv"
ZIPPED_FILE_EXTENSION = ".gzip"

ACQUIRER_CODE = "99999"
PERSON_NATURAL_LEGAL_RATIO = 3


class Registryreports:
    """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Acquirer"""

    def __init__(self, args):
        self.args = args

    def synthetic_reports(self):
        """Produces a synthetic version of the CSV file produced by the acquirers for RTD

        Parameters:
            --res-qty: the number of results generated
            -o, --out-dir: path to the directory where the file will be created, default is "."
            --acquirer: ABI of the sender, default is "99999"
        """

        if not self.args.rep_qty:
            raise ValueError("--res-qty is mandatory")

        reports = []

        for i in range(self.args.rep_qty):
            reports.append(
                [
                    sha256(f"{'terminal_id'}{i}".encode()).hexdigest(),
                    sha256(f"{'merchant_id'}{i}".encode()).hexdigest(),
                    "CF" + str(i).zfill(15 - len(str(i))) if i % PERSON_NATURAL_LEGAL_RATIO == 0 else "PI" + str(
                        i).zfill(10 - len(str(i)))
                ])

        columns = [
            "terminal_id",
            "merchant_id",
            "anagrafica"
        ]
        reports_df = pd.DataFrame(reports, columns=columns)
        reports_df_path = self.args.out_dir + "/" + APPLICATION_PREFIX_FILE_NAME + "." + str(
            self.args.acquirer) + "." + ADE_ACK_FIXED_SEGMENT + "." + datetime.today().strftime(
            '%Y%m%d.%H%M%S') + ".001" + RESULTS_FILE_EXTENSION

        os.makedirs(os.path.dirname(reports_df_path), exist_ok=True)

        with open(reports_df_path, "a") as f:
            f.write(reports_df.to_csv(index=False, header=False, sep=CSV_SEPARATOR))

        print("Done")
