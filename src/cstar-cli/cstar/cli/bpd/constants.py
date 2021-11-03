WINNING_TRANSACTION_SCHEMA = ['acquirer_c', 'trx_timestamp_t', 'hpan_s', 
      'operation_type_c', 'circuit_type_c', 'amount_i', 'amount_currency_c', 
      'mcc_c', 'mcc_descr_s', 'score_n', 'award_period_id_n', 'insert_date_t',
      'insert_user_s', 'update_date_t','update_user_s', 'enabled_b', 'merchant_id_s',
      'correlation_id_s', 'acquirer_id_s', 'id_trx_issuer_s', 'id_trx_acquirer_s',
      'bin_s', 'terminal_id_s', 'fiscal_code_s', 'elab_ranking_new_b', 'elab_ranking_b']

CITIZEN_RANKING_SCHEMA = ['fiscal_code_c', 'award_period_id_n', 'cashback_n', 'insert_date_t',
  'insert_user_s', 'update_date_t', 'update_user_s', 'transaction_n',
  'ranking_n','id_trx_pivot', 'cashback_norm_pivot', 'id_trx_min_transaction_number', 'last_trx_timestamp_t']

CITIZEN_RANKING_EXT_SCHEMA = [
  'award_period_id_n', 'max_transaction_n', 'min_transaction_n',
  'total_participants','ranking_min_n','period_cashback_max_n','insert_date_t',
  'insert_user_s','update_date_t','update_user_s'
]

ACQUIRER_CODES = [ '02008', '32875', '03268', 'EVODE', '01005', '36019', 'STPAY', 'COBAN' ]
ACQUIRER_ID = [ '02008', '429765', '459814', '434495', '459834', 'ACQ001', '493500', '01002132', '09509']
CIRCUIT_TYPES = ['02', '10', '09', '00', '01', '03']
BIN = ['006150', '003062', '005034', '003111', '000000', '00423067', '53567701', '00526211', '51679500',
  '005387', '42306725', '00453997']