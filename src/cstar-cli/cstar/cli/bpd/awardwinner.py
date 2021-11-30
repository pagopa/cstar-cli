import psycopg2
import psycopg2.extras

import pandas as pd
import pandas.io.sql as psql
import random
from datetime import timedelta, datetime, date
import string
from .constants import  CITIZEN_RANKING_EXT_SCHEMA


SELECT_BPD_AWARD_WINNER = """
select
  bcr.award_period_id_n,
  bcr.fiscal_code_c as fiscal_code,
  bc.payoff_instr_s as payoff_instr,
	1500 as amount_n,
	CURRENT_TIMESTAMP as insert_date_t,
	'update_bpd_award_winner_supercashback' as insert_user_s,
	true as enabled_b,
	bap.aw_period_start_d,
	bap.aw_period_end_d,
	1500 as jackpot_n,
	0 as cashback_n,
	'02' as typology_s,
	bc.account_holder_cf_s,
	bc.account_holder_name_s,
	bc.account_holder_surname_s,
	bc.check_instr_status_s,
	bc.technical_account_holder_s,
	bc.issuer_card_id_s
from
	bpd_citizen.bpd_citizen_ranking bcr
	inner join bpd_citizen.bpd_citizen bc on
	bcr.fiscal_code_c = bc.fiscal_code_s
	inner join bpd_award_period.bpd_award_period bap on
	bcr.award_period_id_n = bap.award_period_id_n
	inner join bpd_citizen.bpd_ranking_ext bre on
	bcr.award_period_id_n = bre.award_period_id_n
where
	bcr.award_period_id_n = %(award_period)s
	and bcr.transaction_n >= bap.trx_volume_min_n
	and bc.enabled_b = true
  and bcr.ranking_n <= %(top_n)s;
"""


UPDATE_BPD_AWARD_WINNER = """
insert into bpd_citizen.bpd_award_winner(
	award_period_id_n,
	fiscal_code_s,
	payoff_instr_s,
	amount_n,
	insert_date_t,
	insert_user_s,
	enabled_b,
	aw_period_start_d,
	aw_period_end_d,
	jackpot_n,
	cashback_n,
	typology_s,
	account_holder_cf_s,
	account_holder_name_s,
	account_holder_surname_s,
	check_instr_status_s,
	technical_account_holder_s,
	issuer_card_id_s
)
""" +  SELECT_BPD_AWARD_WINNER 


EXTRACT_JACKPOT_WINNERS = """
 select {} 
 from bpd_citizen.bpd_award_winner 
 where award_period_id_n = %(award_period)s
 and insert_user_s = 'update_bpd_award_winner_supercashback'
 and fiscal_code_s in (

select
  bcr.fiscal_code_c 
from
	bpd_citizen.bpd_citizen_ranking bcr
	inner join bpd_citizen.bpd_citizen bc on
	bcr.fiscal_code_c = bc.fiscal_code_s
	inner join bpd_award_period.bpd_award_period bap on
	bcr.award_period_id_n = bap.award_period_id_n
	inner join bpd_citizen.bpd_ranking_ext bre on
	bcr.award_period_id_n = bre.award_period_id_n
where
	bcr.award_period_id_n = %(award_period)s
	and bcr.transaction_n >= bap.trx_volume_min_n
	and bc.enabled_b = true
  and bcr.ranking_n <= %(top_n)s
  ){}
"""

class Awardwinner() :
  
  def __init__(self, args): 
    self.args = args
    self.db_connection = psycopg2.connect(args.connection_string)
  
  def create_winners(self):
    self.db_cursor = self.db_connection.cursor()

    award_winner_q = self.db_cursor.mogrify(
      SELECT_BPD_AWARD_WINNER,
      {
        "award_period" : self.args.award_period,
        "top_n" : 100000,
      }
    )

    award_winner_df = pd.read_sql(award_winner_q, self.db_connection)
    print(award_winner_df.to_csv())

  def update_jackpot_winners(self):
    self.db_cursor = self.db_connection.cursor()
    update_jackpot_winners_q = self.db_cursor.mogrify(
      UPDATE_BPD_AWARD_WINNER,
      {
        "award_period" : self.args.award_period,
        "top_n" : 100000,
      })

    self.db_cursor.execute(update_jackpot_winners_q)
    self.db_connection.commit()
    self.db_cursor.close()
  
  def extract_jackpot_winners(self):
    self.db_cursor = self.db_connection.cursor()
    jackpot_winners_q = self.db_cursor.mogrify(
      EXTRACT_JACKPOT_WINNERS.format("*", ";"),
      {
        "award_period" : self.args.award_period,
        "top_n" : 100000,
      })
    jackpot_winners_df = pd.read_sql(jackpot_winners_q, self.db_connection)
    jackpot_winners_df = jackpot_winners_df.apply(self._set_payment_reason, axis=1)
    jackpot_winners_df = jackpot_winners_df[[ 
      "id_n",
      "fiscal_code_s",
      "payoff_instr_s",
      "account_holder_name_s",
      "account_holder_surname_s",
      "amount_n",
      "pay_reason",
      "typology_s",
      "award_period_id_n",
      "aw_period_start_d",
      "aw_period_end_d",
      "cashback_n",
      "jackpot_n",
      "check_instr_status_s",
      "technical_account_holder_s"]]
    jackpot_winners_df = jackpot_winners_df.apply(self._convert_award_period_dates, axis=1)
    jackpot_winners_df = jackpot_winners_df.apply(self._amounts_to_cents, axis=1)
    jackpot_winners_df = jackpot_winners_df.apply(self._pad_award_period, axis=1)


    print(jackpot_winners_df.to_csv(index=False, header=False, sep=";"))
  
  def send_jackpot_winners(self):
    db_cursor = self.db_connection.cursor()
    table = "bpd_citizen.bpd_award_winner"
    set_values = "chunk_filename_s = %(filename)s , status_s = 'SENT' "
    conditions = "id_n in ({})".format(EXTRACT_JACKPOT_WINNERS.format("id_n", ""))
    update = "UPDATE {} SET {} WHERE {};".format(
        table, set_values, conditions)
    send_jackpot_winners_q = db_cursor.mogrify(update, 
      {
        "award_period" : self.args.award_period,
        "top_n" : 100000,
        "filename" : self.args.chunk_file_name
      })
    print(send_jackpot_winners_q)
    db_cursor.execute(send_jackpot_winners_q)
    print("rowcount ", db_cursor.rowcount)
    self.db_connection.commit()
    db_cursor.close()
  
  def read_state_41(self):
    transfers_df = pd.read_csv(self.args.file, sep=';')
    transfers_df = transfers_df.apply(self._extract_transfer_id, axis=1)
    assert transfers_df.idKey.size == transfers_df.idKey.unique().size, "idKey not unique"

    transfers_df = transfers_df[:5]
    print(transfers_df)

    pagopa_transfers_q = self.db_connection.cursor().mogrify(
      "SELECT * "
      "FROM bpd_citizen.bpd_award_winner " 
      "WHERE id_n in %(id_n_list)s;",
      {
        "id_n_list": tuple(transfers_df.idKey.unique()),
      }
    )

    pagopa_transfers_df = pd.read_sql(pagopa_transfers_q, self.db_connection)
    pagopa_transfers_df['id_n'] = pagopa_transfers_df['id_n'].astype(str)

    pagopa_n_tranfers_per_awp_q = self.db_connection.cursor().mogrify(
      "SELECT baw.id_n, C.pagopa_n_tranfers_per_awp "
      "FROM bpd_citizen.bpd_award_winner baw "
      "INNER JOIN "
      "(SELECT fiscal_code_s, award_period_id_n, count(fiscal_code_s) AS pagopa_n_tranfers_per_awp "
      "   FROM bpd_citizen.bpd_award_winner "
      "   WHERE id_n in %(id_n_list)s "
      "   GROUP BY (fiscal_code_s, award_period_id_n) ) C "
      "ON baw.fiscal_code_s = C.fiscal_code_s "
      "AND baw.award_period_id_n = C.award_period_id_n",
      {
        "id_n_list": tuple(transfers_df.idKey.unique()),
      }
    )

    pagopa_n_tranfers_per_awp_df = pd.read_sql(pagopa_n_tranfers_per_awp_q, self.db_connection)
    pagopa_n_tranfers_per_awp_df['id_n'] = pagopa_n_tranfers_per_awp_df['id_n'].astype(str)

    transfers_df = transfers_df.set_index('idKey').join(pagopa_transfers_df.set_index('id_n'))
    transfers_df = transfers_df.join(pagopa_n_tranfers_per_awp_df.set_index('id_n'))

    transfers_df['consap_n_occurrencies'] = ( transfers_df
      .groupby('fiscalCode')['amount']
      .transform('size') )

    print(transfers_df.to_csv(sep=';'))

  def _extract_transfer_id(self, transfer):
    transfer.idKey = str(int(transfer.idKey[2:]))
    return transfer
  
  def _convert_award_period_dates(self, winner):
    winner.aw_period_start_d = winner.aw_period_start_d.strftime("%d/%m/%Y")
    winner.aw_period_end_d = winner.aw_period_end_d.strftime("%d/%m/%Y")

    return winner
  
  def _pad_award_period(self, winner):
    winner.award_period_id_n = '%02d' % winner.award_period_id_n
    return winner
  
  def _amounts_to_cents(self, winner):
    winner.amount_n = int(winner.amount_n * 100)
    winner.amount_n = winner.amount_n if winner.amount_n >= 100 else '%03d' % winner.amount_n
    winner.cashback_n = int(winner.cashback_n * 100)
    winner.cashback_n = winner.cashback_n if winner.cashback_n >= 100 else '%03d' % winner.cashback_n
    winner.jackpot_n = int(winner.jackpot_n * 100)
    winner.jackpot_n = winner.jackpot_n if winner.jackpot_n >= 100 else '%03d' % winner.jackpot_n
    return winner

  def _set_payment_reason(self, winner):
    pay_reason = "%09d - Cashback di Stato - dal %s  al %s" % (winner.id_n, 
      winner.aw_period_start_d.strftime("%d/%m/%Y"), winner.aw_period_end_d.strftime("%d/%m/%Y"))
    
    if winner.technical_account_holder_s is not None or winner.account_holder_cf_s != winner.fiscal_code_s :
      pay_reason += " - %s" % winner.fiscal_code_s
    
    if winner.technical_account_holder_s is not None and winner.issuer_card_id_s is not None :
      pay_reason += " - %s" % winner.issuer_card_id_s

    winner['pay_reason'] = pay_reason
    return winner


