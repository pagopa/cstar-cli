import psycopg2
import psycopg2.extras

import pandas as pd
import pandas.io.sql as psql
import random
from datetime import timedelta, datetime, date
import string
from .constants import  CITIZEN_RANKING_EXT_SCHEMA


class Awardperiod() :
  def __init__(self, args):
    self.args = args
    self.db_connection = psycopg2.connect(args.connection_string)

  def set_grace_period(self):
    table = "bpd_award_period.bpd_award_period"
    set_values = "aw_grace_period_n = (%s)"
    conditions = "award_period_id_n = (%s)"
    update_q = "UPDATE {} SET {} WHERE {};".format(
         table, set_values, conditions)

    cursor = self.db_connection.cursor()
    cursor.execute(update_q, [self.args.grace_period, self.args.id])
    self.db_connection.commit()
    cursor.close()

  def set_properties(self):

    award_period_df = self._read_award_period()
    award_period_start = award_period_df.at[0,'aw_period_start_d']
    delta = date.today() - award_period_start
    insert_datetime = ( datetime.combine( award_period_start, datetime.min.time())
      + timedelta(seconds=random.random() * delta.total_seconds()) )

    award_period_ext_df = pd.DataFrame(columns=CITIZEN_RANKING_EXT_SCHEMA)
    award_period_ext_df = award_period_ext_df.append({
        'award_period_id_n' : self.args.id,
        'max_transaction_n' : 2000,
        'min_transaction_n' : 0,
        'total_participants' : 10000000,
        'ranking_min_n': 0,
        'period_cashback_max_n' : f'{150:.2f}',
        'insert_date_t': insert_datetime.isoformat(),
        'insert_user_s': 'PAGOPATEST',
        'update_date_t' : None,
        'update_user_s' : None
    }, True)


    if len(award_period_ext_df) > 0:

      columns = list(award_period_ext_df)

      # create VALUES('%s', '%s",...) one '%s' per column
      set_values = ",".join(["{} = (%s)".format(_) for _ in columns])

      #create INSERT INTO table (columns) VALUES('%s',...)
      update = "UPDATE {} SET {} WHERE award_period_id_n = {};".format(
        "bpd_citizen.bpd_ranking_ext", set_values, self.args.id)

      cursor = self.db_connection.cursor()
      psycopg2.extras.execute_batch(cursor, update, award_period_ext_df.values)
      self.db_connection.commit()
      cursor.close()

  def _read_award_period(self) :
    self.db_cursor = self.db_connection.cursor()

    award_period_q = self.db_cursor.mogrify(
      "SELECT * "
      "FROM bpd_award_period.bpd_award_period "
      "WHERE award_period_id_n = %(id)s;", {"id": self.args.id})

    return pd.read_sql(award_period_q, self.db_connection)

  def read_all(self) :
    self.db_cursor = self.db_connection.cursor()

    award_period_q = self.db_cursor.mogrify(
      "SELECT award_period_id_n, aw_period_start_d, aw_period_end_d "
      "FROM bpd_award_period.bpd_award_period ")
    print(pd.read_sql(award_period_q, self.db_connection))
