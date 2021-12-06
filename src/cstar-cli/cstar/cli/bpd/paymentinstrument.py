import psycopg2
import pandas as pd
import uuid


class Paymentinstrument():

  def __init__(self, args):
    self.args = args
    self.db_connection = psycopg2.connect(args.connection_string)
  
  def enroll(self):
    
    payment_instruments_df = pd.read_csv(self.args.file, sep=';')
    if payment_instruments_df.shape[1] != 4:
      raise ValueError(f"Invalid number of column in input file (expected 4, found {payment_instruments_df.shape[1]})")

    insert_id = uuid.uuid4()

    cursor = self.db_connection.cursor()

    for index, row in payment_instruments_df.iterrows():

      print(f"Processing row {index}")

      insert_payment_instrument_q = cursor.mogrify(
        "INSERT INTO bpd_payment_instrument.bpd_payment_instrument "
        "  (hpan_s, fiscal_code_s, enrollment_t, status_c, insert_user_s) "
        "VALUES (%(hpan)s, %(fiscal_code)s, %(enrollment)s, 'ACTIVE', %(insert_user)s)",
        {
          "hpan": row.hpan,
          "fiscal_code": row.fiscal_code,
          "enrollment": row.enrollment,
          "insert_user": str(insert_id)
        }
      )

      print(f"Executing query: {insert_payment_instrument_q}")
      cursor.execute(insert_payment_instrument_q)

      insert_payment_instrument_history_q = cursor.mogrify(
        "INSERT INTO bpd_payment_instrument.bpd_payment_instrument_history "
        "  (hpan_s, activation_t, insert_user_s)"
        "VALUES (%(hpan)s, %(activation)s, %(insert_user)s)",
        {
          "hpan": row.hpan,
          "activation": row.activation,
          "insert_user": str(insert_id)
        }
      )

      print(f"Executing query: {insert_payment_instrument_history_q}")
      cursor.execute(insert_payment_instrument_history_q)
    
    self.db_connection.commit()
    cursor.close()