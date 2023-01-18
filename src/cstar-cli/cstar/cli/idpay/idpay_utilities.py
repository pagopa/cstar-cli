import os

import pandas as pd
from dateutil import parser

CSV_SEPARATOR = ";"

def is_iso8601(date_to_check):
    try:
        parser.parse(date_to_check)
        return True
    except ValueError:
        return False
def serialize(dataset, columns, destination_path):
    dataset_dataframe = pd.DataFrame(dataset, columns=columns)
    trx_file_path = os.path.join(destination_path, )

    os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

    with open(trx_file_path, "a") as f:
        f.write(dataset_dataframe.to_csv(index=False, header=False, sep=CSV_SEPARATOR))


def flatten(dataset):
    res = []
    for i in dataset:
        for j in dataset[i]:
            res.append([i, j])
    return res


def flatten_values(dataset):
    res = []
    for i in dataset:
        for j in dataset[i]:
            res.append(j)
    return res
