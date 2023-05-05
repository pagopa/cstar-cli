import csv
import os
import random
from datetime import timedelta

import pgpy
import pandas as pd
from dateutil import parser

CSV_SEPARATOR = ";"
ENCRYPTED_FILE_EXTENSION = "pgp"

def is_iso8601(date_to_check):
    try:
        parser.parse(date_to_check)
        return True
    except ValueError:
        return False


def serialize(dataset, columns, destination_path, have_header=False):
    dataset_dataframe = pd.DataFrame(dataset, columns=columns)
    trx_file_path = os.path.join(destination_path, )
    os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

    with open(trx_file_path, "a", newline='') as f:
        f.write(dataset_dataframe.to_csv(index=False, header=have_header, sep=CSV_SEPARATOR, lineterminator='\n'))


def deserialize(source_file):
    with open(source_file, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        data = []
        for row in reader:
            data.append({row[0]: row[1]})

    result = {k: v for d in data for k, v in d.items()}

    return result

def deserialize_trx(source_file):
    with open(source_file, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        data = {}
        for row in reader:
            data[row[0]] = []
            for el in row[1:]:
                data[row[0]].append(el)

    return data


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


def pgp_string(payload: str, pgp_key_data: str):
    key = pgpy.PGPKey.from_blob(pgp_key_data)
    message = pgpy.PGPMessage.new(payload)
    ciphertext = key[0].encrypt(message, version=b'BCPG v1.58')
    return str(ciphertext)


def pgp_file(file_path: str, pgp_key_data: str):
    key = pgpy.PGPKey.from_blob(pgp_key_data)
    with open(file_path, "rb") as f:
        message = pgpy.PGPMessage.new(f.read(), file=True)
    encrypted = key[0].encrypt(message, openpgp=True)
    output_path = f"{file_path}.{ENCRYPTED_FILE_EXTENSION}"
    with open(output_path, "wb") as f:
        f.write(bytes(encrypted))

    return output_path

def random_date(start, end):
    delta_seconds = int((end - start).total_seconds())
    if delta_seconds < 0:
        print(f'Error: end date prior to start date')
        exit(1)
    return start + timedelta(
        seconds=random.randint(0, delta_seconds)
    )
