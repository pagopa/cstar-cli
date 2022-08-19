import psycopg2
import psycopg2.extras
import pandas as pd
import uuid


class Paymentinstrument():

  def __init__(self, args):
    self.args = args
    self.db_connection = psycopg2.connect(args.connection_string)

  def enroll(self):

    payment_instruments_df = pd.read_csv(self.args.file, sep=";")
    if payment_instruments_df.shape[1] != 4:
      raise ValueError(f"Invalid number of column in input file (expected 4, found {payment_instruments_df.shape[1]})")

    insert_id = uuid.uuid4()

    cursor = self.db_connection.cursor()

    sql =  "INSERT INTO bpd_payment_instrument.bpd_payment_instrument "
    sql += "(hpan_s, fiscal_code_s, enrollment_t, status_c, insert_user_s) "
    sql += "VALUES (%s, %s, %s, 'ACTIVE', '" + str(insert_id) + "') "
    sql += "ON CONFLICT DO NOTHING"
    values_from_cols = ["hpan", "fiscal_code", "enrollment"]
    psycopg2.extras.execute_batch(cursor, sql, payment_instruments_df[values_from_cols].values, page_size=1000)

    sql =  "INSERT INTO bpd_payment_instrument.bpd_payment_instrument_history "
    sql += "(hpan_s, activation_t, insert_user_s) "
    sql += "VALUES (%s, %s, '" + str(insert_id) + "') "
    sql += "ON CONFLICT DO NOTHING"
    values_from_cols = ["hpan", "activation"]
    psycopg2.extras.execute_batch(cursor, sql, payment_instruments_df[values_from_cols].values, page_size=1000)

    self.db_connection.commit()
    cursor.close()
