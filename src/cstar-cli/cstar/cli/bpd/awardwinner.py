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