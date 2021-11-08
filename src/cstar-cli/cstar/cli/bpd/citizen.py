import psycopg2
import psycopg2.extras

import pandas as pd
import pandas.io.sql as psql
import random
from datetime import timedelta, datetime, date
import string
from .constants import WINNING_TRANSACTION_SCHEMA, CITIZEN_RANKING_SCHEMA, ACQUIRER_CODES, CIRCUIT_TYPES, ACQUIRER_ID, BIN



class Citizen():
  def __init__(self, args):
    self.args = args
    self.db_connection = psycopg2.connect(args.connection_string)
  
  def check_ranking(self):
    citizens_df = (pd.read_csv(self.args.file, sep=';')
      .groupby(by='fiscal_code_s')
      .count()
      .rename(columns={'trx_date_t': 'new_transactions'})[['new_transactions']])
    citizens_df['fiscal_code_s'] = citizens_df.index

    current_ranking = lambda x : self._read_current_ranking(x)
    citizens_df = citizens_df.apply(current_ranking, axis=1)
    
    next_ranking = lambda x : self._read_next_ranking(x)
    citizens_df = citizens_df.apply(next_ranking, axis=1)

    print(citizens_df[(citizens_df['ranking_n'] > 100000) & (citizens_df['best_new_ranking_n']  <= 100000)].to_csv())

  
  def _read_current_ranking(self, citizen):
    self.db_cursor = self.db_connection.cursor()

    ranking_q = self.db_cursor.mogrify(
      "SELECT transaction_n, ranking_n "
      "FROM bpd_citizen.bpd_citizen_ranking " 
      "WHERE fiscal_code_c = %(fiscal_code)s "
      "AND award_period_id_n = %(award_period)s ;",
      {
        "fiscal_code": citizen.fiscal_code_s,
        "award_period" : self.args.award_period
      }
    )

    ranking_df = pd.read_sql(ranking_q, self.db_connection)
    assert ranking_df.shape[0] == 1, "Ranking not unique"

    citizen['transaction_n'] = ranking_df.at[0, 'transaction_n']
    citizen['ranking_n'] = ranking_df.at[0, 'ranking_n']

    return citizen

  def _read_next_ranking(self, citizen):
    self.db_cursor = self.db_connection.cursor()

    ranking_q = self.db_cursor.mogrify(
      "SELECT ranking_n "
      "FROM bpd_citizen.bpd_citizen_ranking " 
      "WHERE transaction_n = %(transaction_n)s + %(new_transactions)s"
      "AND award_period_id_n = %(award_period)s ;",
      {
        "transaction_n" : citizen.transaction_n,
        "new_transactions" : citizen.new_transactions,
        "award_period" : self.args.award_period
      }
    )

    ranking_df = pd.read_sql(ranking_q, self.db_connection)
    citizen['best_new_ranking_n'] = ranking_df['ranking_n'].min().astype(int)
    citizen['worst_new_ranking_n'] = ranking_df['ranking_n'].max().astype(int)

    return citizen
