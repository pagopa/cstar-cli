import psycopg2
import psycopg2.extras

import pandas as pd
import pandas.io.sql as psql
import random
from datetime import timedelta, datetime, date
import string
from .constants import WINNING_TRANSACTION_SCHEMA, CITIZEN_RANKING_SCHEMA, ACQUIRER_CODES, CIRCUIT_TYPES, ACQUIRER_ID, BIN



class Transaction():
  def __init__(self, args):
    self.args = args
    self.db_connection = psycopg2.connect(args.connection_string)

  def generate(self):

    award_period_df = self._read_award_period()
    assert award_period_df.shape[0] > 0, "Award Period n. %s doesn't exist." % (self.args.award_period)

    citizen_df = self._read_fiscal_code()
    assert citizen_df.shape[0] > 0, "Citizen %s is not onboarded." % (self.args.fiscal_code)

    payment_instrument_df = self._read_enrolled_payment_instruments()
    assert payment_instrument_df.shape[0] > 0, "Citizen %s didn't enrolled payment instruments" % (self.args.fiscal_code)


    transactions_df = pd.DataFrame(columns=WINNING_TRANSACTION_SCHEMA)
    for _ in range(self.args.number) :
      my_transaction = self._generate_single_transaction(award_period_df,
        citizen_df, hpan=payment_instrument_df.at[0, 'hpan_s'])

      transactions_df = transactions_df.append(my_transaction, True)


    # Write Transactions in Winning Transactions
    self._create_transactions(transactions_df)

  def enable(self):

    award_period_df = self._read_award_period()
    assert award_period_df.shape[0] > 0, "Award Period n. %s doesn't exist." % (self.args.award_period)

    citizen_df = self._read_fiscal_code()
    assert citizen_df.shape[0] > 0, "Citizen %s is not onboarded." % (self.args.fiscal_code)


    transactions_disabled_df = self._read_disabled_transactions()
    print(transactions_disabled_df)

    table = "bpd_winning_transaction.bpd_winning_transaction"

    set_values = (
      "update_date_t = (%s), "
      "update_user_s = (%s), "
      "enabled_b = (%s) ")

    conditions = (
      "award_period_id_n = (%s) AND "
      "fiscal_code_s = (%s) AND "
      "update_date_t > (%s) AND "
      "enabled_b = false"
    )

    #   #create INSERT INTO table (columns) VALUES('%s',...)
    update_q = "UPDATE {} SET {} WHERE {};".format(
         table, set_values, conditions)

    cursor = self.db_connection.cursor()
    cursor.execute(update_q, ['now()', self.args.update_user, "true", self.args.award_period, self.args.fiscal_code, self.args.from_date])
    self.db_connection.commit()
    cursor.close()


  def update_ranking(self) :
     # Must read all transactions
    summary_df = self._summarize_ranking_by_fiscal_code()

    ranking_df = pd.DataFrame(columns=CITIZEN_RANKING_SCHEMA).append(
      {
        'fiscal_code_c' : self.args.fiscal_code,
        'award_period_id_n' : self.args.award_period,
        'cashback_n': summary_df.at[0, 'score'],
        'insert_date_t' : datetime.now().isoformat(),
        'insert_user_s' : "PAGOPATEST",
        'update_date_t' : None,
        'update_user_s' : None,
        'transaction_n' : summary_df.at[0, 'transactions_num'],
        'ranking_n' : random.randint(0, 100000),
        'id_trx_pivot' : None,
        'cashback_norm_pivot' : None,
        'id_trx_min_transaction_number' : None,
        'last_trx_timestamp_t' : None
      }
      , True)
    self._update_ranking(ranking_df)

  def check(self):
    transactions_df = pd.read_csv(self.args.file, sep=';')

    match = lambda x : self._read_matching_transactions(x)

    print(transactions_df.apply(match, axis=1))

  def check_unique(self):
    transactions_df = pd.read_csv(self.args.file, sep=';', dtype={"operation_type_c": str, "acquirer_id_s" : str})
    transactions_df["unique"] = False
    check_unique = lambda x : self._read_unique_transaction(x)
    transactions_df = transactions_df.apply(check_unique, axis=1)
    result = transactions_df[transactions_df["unique"] == False]
    if(result.shape[0] > 0 ):
      print(result.to_csv())
    else :
      print ("Check OK")

  def _read_unique_transaction(self, transaction):
    self.db_cursor = self.db_connection.cursor()

    transactions_unique_q = self.db_cursor.mogrify(
      "SELECT * "
      "FROM bpd_winning_transaction.bpd_winning_transaction "
      "WHERE trx_timestamp_t = %(trx_timestamp)s "
      "AND id_trx_acquirer_s = %(id_trx_acquirer)s "
      "AND acquirer_c = %(acquirer_c)s "
      "AND acquirer_id_s = %(acquirer_id)s "
      "AND operation_type_c = %(operation_type)s;",
      {
        "trx_timestamp": transaction.trx_timestamp_t,
        "id_trx_acquirer" : transaction.id_trx_acquirer_s,
        "acquirer_c" : transaction.acquirer_c,
        "acquirer_id" : transaction.acquirer_id_s,
        "operation_type" : transaction.operation_type_c
      })

    transaction_db = pd.read_sql(transactions_unique_q, self.db_connection)
    transaction["unique"] = transaction_db.shape[0] == 1

    return transaction

  def _read_transactions_by_fiscal_code(self) :
    self.db_cursor = self.db_connection.cursor()

    transactions_q = self.db_cursor.mogrify(
      "SELECT * "
      "FROM bpd_winning_transaction.bpd_winning_transaction "
      "WHERE fiscal_code_s = %(fiscal_code)s "
      "AND enabled_b = true;", {"fiscal_code": self.args.fiscal_code})

    return pd.read_sql(transactions_q, self.db_connection)



  def _read_matching_transactions (self, transaction):

    print("\n===========\nTO MATCH: ", transaction)

    self.db_cursor = self.db_connection.cursor()


    transactions_match_q = self.db_cursor.mogrify(
      "SELECT trx_timestamp_t, amount_i, fiscal_code_s, id_trx_acquirer_s, id_trx_issuer_s "
      "FROM bpd_winning_transaction.bpd_winning_transaction "
      "WHERE fiscal_code_s = %(fiscal_code)s "
      # "AND DATE_PART('day', trx_timestamp_t - %(trx_date)s) = 0 "
      "AND id_trx_acquirer_s = %(id_trx_acquirer)s ;",
      # "AND amount_i = %(amount)s ;",
      #"AND enabled_b = true;",
      {
        "fiscal_code": transaction.fiscal_code_s.strip(),
        "trx_date": datetime.strptime(transaction.trx_date_t, "%m/%d/%y").date().isoformat(),
        "amount" : transaction.amount_i,
        "id_trx_acquirer" : transaction.id_trx_acquirer_s.strip()
      }
    )

    print("MATCHED: ")
    if not pd.isna(transaction.id_trx_acquirer_s):
      print(pd.read_sql(transactions_match_q, self.db_connection))



  def _summarize_ranking_by_fiscal_code(self) :

    ranking_summary_q = self.db_cursor.mogrify(
      "SELECT sum(amount_i) AS amount, sum(score_n) AS score, count(*) AS transactions_num "
      "FROM bpd_winning_transaction.bpd_winning_transaction "
      "WHERE fiscal_code_s = %(fiscal_code)s "
      "AND enabled_b = true "
      "GROUP BY fiscal_code_s;", {"fiscal_code": self.args.fiscal_code})

    return pd.read_sql(ranking_summary_q, self.db_connection)

  def _update_ranking(self, ranking_df):
    if len(ranking_df) > 0:

      columns = list(ranking_df)

      # create VALUES('%s', '%s",...) one '%s' per column
      values = "VALUES({})".format(",".join(["%s" for _ in columns]))

      #create INSERT INTO table (columns) VALUES('%s',...)
      insert = "INSERT INTO {} ({}) {}".format(
        "bpd_citizen.bpd_citizen_ranking", ",".join(columns), values)

      cursor = self.db_connection.cursor()
      psycopg2.extras.execute_batch(cursor, insert, ranking_df.values)
      self.db_connection.commit()
      cursor.close()

  def _read_award_period(self) :
    self.db_cursor = self.db_connection.cursor()

    award_period_q = self.db_cursor.mogrify(
      "SELECT * "
      "FROM bpd_award_period.bpd_award_period "
      "WHERE award_period_id_n = %(id)s;", {"id": self.args.award_period})

    return pd.read_sql(award_period_q, self.db_connection)

  def _read_fiscal_code(self) :
    self.db_cursor = self.db_connection.cursor()

    citizen_q = self.db_cursor.mogrify(
      "SELECT * "
      "FROM bpd_citizen.bpd_citizen "
      "WHERE fiscal_code_s = %(fiscal_code)s "
      "AND enabled_b = true", {"fiscal_code": self.args.fiscal_code})

    return pd.read_sql(citizen_q, self.db_connection)

  def _read_enrolled_payment_instruments(self) :
    self.db_cursor = self.db_connection.cursor()

    payment_instruments_q = self.db_cursor.mogrify(
      "SELECT hpan_s, fiscal_code_s "
      "FROM bpd_payment_instrument.bpd_payment_instrument "
      "WHERE fiscal_code_s = %(fiscal_code)s "
      "AND enabled_b = true", {"fiscal_code": self.args.fiscal_code})

    return pd.read_sql(payment_instruments_q, self.db_connection)



  def _read_disabled_transactions(self):
    self.db_cursor = self.db_connection.cursor()

    transactions_disabled_q = self.db_cursor.mogrify(
      "SELECT update_date_t, fiscal_code_s "
      "FROM bpd_winning_transaction.bpd_winning_transaction "
      "WHERE fiscal_code_s = %(fiscal_code)s "
      "AND update_date_t > %(from_date)s"
      "AND award_period_id_n = %(award_period)s"
      "AND enabled_b = false;",
      {
        "fiscal_code": self.args.fiscal_code,
        "from_date": self.args.from_date,
        "award_period" : self.args.award_period
      }
    )

    return pd.read_sql(transactions_disabled_q, self.db_connection)

  def _create_transactions(self, transactions_df):
    if len(transactions_df) > 0:

      columns = list(transactions_df)

      # create VALUES('%s', '%s",...) one '%s' per column
      values = "VALUES({})".format(",".join(["%s" for _ in columns]))

      #create INSERT INTO table (columns) VALUES('%s',...)
      insert = "INSERT INTO {} ({}) {}".format(
        "bpd_winning_transaction.bpd_winning_transaction", ",".join(columns), values)

      cursor = self.db_connection.cursor()
      psycopg2.extras.execute_batch(cursor, insert, transactions_df.values)
      self.db_connection.commit()
      cursor.close()

  def _generate_single_transaction(self, award_period_df, citizen_df, hpan) :
    amount = random.random() * 100
    id_trx = list(''.join(random.choice(string.ascii_letters) for _ in range(2))
      + ''.join(random.choice(string.digits) for _ in range(4)))
    random.shuffle(id_trx)
    award_period_start = award_period_df.at[0,'aw_period_start_d']
    delta = date.today() - award_period_start
    trx_time = ( datetime.combine( award_period_start, datetime.min.time())
      + timedelta(seconds=random.random() * delta.total_seconds()) )
    insert_time = trx_time + timedelta(days=random.randint(0,5), seconds=random.random() * 3600 * 24)

    assert trx_time <= insert_time

    return {
      'acquirer_c' : random.choice(ACQUIRER_CODES),
      'trx_timestamp_t': trx_time.isoformat(),
      'hpan_s': hpan,
      'operation_type_c': '00',
      'circuit_type_c': random.choice(CIRCUIT_TYPES),
      'amount_i': f'{amount:.2f}',
      'amount_currency_c': '978',
      'mcc_c': '0000',
      'mcc_descr_s' : None,
      'score_n' : f'{0.1 * amount:.2f}',
      'award_period_id_n' : self.args.award_period,
      'insert_date_t' : insert_time.isoformat(),
      'insert_user_s' : 'PAGOPATEST',
      'update_date_t' : None,
      'update_user_s' : None,
      'enabled_b' : True,
      'merchant_id_s' : ''.join(random.choice(string.digits) for _ in range(15)),
      'correlation_id_s': ''.join(random.choice(string.digits) for _ in range(12)),
      'acquirer_id_s' : random.choice(ACQUIRER_ID),
      'id_trx_issuer_s' : ''.join(id_trx).upper(),
      'id_trx_acquirer_s' : ''.join(random.choice(string.digits) for _ in range(12)),
      'bin_s' : random.choice(BIN),
      'terminal_id_s' : ''.join(random.choice(string.digits) for _ in range(8)),
      'fiscal_code_s' : self.args.fiscal_code,
      'elab_ranking_new_b' : True,
      'elab_ranking_b' : True
    }
