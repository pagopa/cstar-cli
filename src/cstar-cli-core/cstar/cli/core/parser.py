import argparse


def parser():
    argparser = argparse.ArgumentParser()
    subsystem_parser = argparser.add_subparsers(dest="subsystem")
    subsystem_parser.required = True

    subsystem_parser.add_parser("fa")

    # BPD
    bpd_parser = subsystem_parser.add_parser("bpd").add_subparsers(dest="command")

    # -TRANSACTION
    bpd_transaction = bpd_parser.add_parser("transaction")

    bpd_transaction.add_argument("--action")
    bpd_transaction.add_argument("--fiscal-code")
    bpd_transaction.add_argument("--environment")
    bpd_transaction.add_argument("--connection-string")
    bpd_transaction.add_argument("--award-period")
    bpd_transaction.add_argument("--number", type=int)
    bpd_transaction.add_argument("--from-date")
    bpd_transaction.add_argument("--update-user")
    bpd_transaction.add_argument("--file")

    # -AWARD PERIOD
    bpd_award_period = bpd_parser.add_parser("awardperiod")

    bpd_award_period.add_argument("--action")
    bpd_award_period.add_argument("--id")
    bpd_award_period.add_argument("--grace-period")
    bpd_award_period.add_argument("--connection-string")

    bpd_award_winner = bpd_parser.add_parser("awardwinner")

    bpd_award_winner.add_argument("--action")
    bpd_award_winner.add_argument("--award-period")
    bpd_award_winner.add_argument("--connection-string")
    bpd_award_winner.add_argument("--file")
    bpd_award_winner.add_argument("--chunk-file-name")
    bpd_award_winner.add_argument("--commit", action="store_true")

    # -CITIZEN
    bpd_transaction = bpd_parser.add_parser("citizen")

    bpd_transaction.add_argument("--action")
    bpd_transaction.add_argument("--fiscal-code")
    bpd_transaction.add_argument("--environment")
    bpd_transaction.add_argument("--connection-string")
    bpd_transaction.add_argument("--award-period")
    bpd_transaction.add_argument("--file")

    # -PAYMENT INSTRUMENT
    bpd_payment_instrument = bpd_parser.add_parser("paymentinstrument")

    bpd_payment_instrument.add_argument("--action")
    bpd_payment_instrument.add_argument("--file")
    bpd_payment_instrument.add_argument("--connection-string")

    # RTD
    rtd_parser = subsystem_parser.add_parser("rtd").add_subparsers(dest="command")

    # -TRANSACTIONS
    rtd_transaction_filter = rtd_parser.add_parser("transactionfilter")

    rtd_transaction_filter.add_argument("--action")
    rtd_transaction_filter.add_argument("--salt", default="SALT876")
    rtd_transaction_filter.add_argument("--sender", default="99999")
    rtd_transaction_filter.add_argument("--pans-prefix", type=str, default="prefix_")
    rtd_transaction_filter.add_argument("--pans-qty", type=int, default=10)
    rtd_transaction_filter.add_argument("--hashpans-qty", type=int)
    rtd_transaction_filter.add_argument("--trx-qty", type=int, default=1)
    rtd_transaction_filter.add_argument("--ratio", type=int, default=1)
    rtd_transaction_filter.add_argument("--pos-number", type=int)
    rtd_transaction_filter.add_argument("--par-ratio", type=int, default=1)
    rtd_transaction_filter.add_argument("--mcc", type=str, default=6010)
    rtd_transaction_filter.add_argument("--pgp", action="store_true")
    rtd_transaction_filter.add_argument("--input-hashpans", type=str, default="")
    rtd_transaction_filter.add_argument("-o", "--out-dir", type=str, default="./generated")
    rtd_transaction_filter.add_argument("--key", type=str, default="./public.key")

    # -CARDS
    rtd_transaction_filter.add_argument("--crd-qty", type=int)
    rtd_transaction_filter.add_argument("--max-num-children", type=int)
    rtd_transaction_filter.add_argument("--num-children", type=int)
    rtd_transaction_filter.add_argument("--par", type=str, default="RANDOM")
    rtd_transaction_filter.add_argument("--version", type=int, default=1)
    rtd_transaction_filter.add_argument("--state", type=str, default="ALL")
    rtd_transaction_filter.add_argument("--revoked-percentage", type=int, default=10)

    # RTD upload
    rtd_transaction_upload = rtd_parser.add_parser("transactionupload")
    rtd_transaction_upload.add_argument("--action", required=True)
    rtd_transaction_upload.add_argument("--env", type=str, default="dev", required=True)
    rtd_transaction_upload.add_argument("--api-key", type=str, default="", required=True)
    rtd_transaction_upload.add_argument("--key", type=str, default="", required=True)
    rtd_transaction_upload.add_argument("--cert", type=str, default="", required=True)
    rtd_transaction_upload.add_argument("--file", type=str, default="", required=True)

    # TAE
    tae_parser = subsystem_parser.add_parser("tae").add_subparsers(dest="command")

    # -TRANSACTION AGGREGATE
    tae_transaction_aggregates = tae_parser.add_parser("transactionaggregate")

    tae_transaction_aggregates.add_argument("--action")
    tae_transaction_aggregates.add_argument("--aggr-qty", type=int)
    tae_transaction_aggregates.add_argument("--sender", default="99999")
    tae_transaction_aggregates.add_argument("--reverse-ratio", type=int)
    tae_transaction_aggregates.add_argument("-o", "--out-dir", type=str, default="./generated")
    tae_transaction_aggregates.add_argument("--pgp", action="store_true")
    tae_transaction_aggregates.add_argument("--shuffle", action="store_true")
    tae_transaction_aggregates.add_argument("--to-ade", action="store_true")
    tae_transaction_aggregates.add_argument("--ratio-dirty-pos-type", type=int)
    tae_transaction_aggregates.add_argument("--ratio-dirty-vat", type=int)
    tae_transaction_aggregates.add_argument("--key", type=str, default="./public.key")

    # -RESULTS
    tae_results = tae_parser.add_parser("results")

    tae_results.add_argument("--action")
    tae_results.add_argument("--res-qty", type=int)
    tae_results.add_argument("-o", "--out-dir", type=str, default="./generated")
    tae_results.add_argument("--gzip", action="store_true")

    # -REPORTS
    tae_reports = tae_parser.add_parser("registryreports")

    tae_reports.add_argument("--action")
    tae_reports.add_argument("--rep-qty", type=int)
    tae_reports.add_argument("--acquirer", default="99999")
    tae_reports.add_argument("-o", "--out-dir", type=str, default="./generated")

    # SENDER
    sender_parser = subsystem_parser.add_parser("sender").add_subparsers(dest="command")

    # -AGGREGATES
    sender_aggregates_parser = sender_parser.add_parser("aggregates")

    sender_aggregates_parser.add_argument("--action", required=True,
                                          help="Action to perform with the invocation of the command")
    sender_aggregates_parser.add_argument("--aggr-qty", type=int, help="Aggregates quantity to generate")
    sender_aggregates_parser.add_argument("--sender", default="99999", help="Sender code")
    sender_aggregates_parser.add_argument("--avg-trx", type=int, default=10,
                                          help="Average transaction number per aggregation")
    sender_aggregates_parser.add_argument("-o", "--out-dir", type=str, default="./generated",
                                          help="Output directory of both files")
    sender_aggregates_parser.add_argument("--shuffle", action="store_true", help="Flag for shuffling transactions file")
    sender_aggregates_parser.add_argument("--ratio-dirty-vat", type=int, default=51)
    sender_aggregates_parser.add_argument("--ratio-dirty-pos-type", type=int, default=50)
    sender_aggregates_parser.add_argument("--pans-prefix", type=str, default="pan")

    # -DIFF CHECKER
    sender_aggregates_parser.add_argument('-f', '--files', nargs=2, help="Files to compare for equality")

    # IDPay
    idpay_parser = subsystem_parser.add_parser("idpay").add_subparsers(dest="command")

    # -Dataset
    idpay_dataset_parser = idpay_parser.add_parser("idpaydataset")
    idpay_dataset_parser.add_argument("--action", required=True,
                                      help="Action to perform with the invocation of the command")
    idpay_dataset_parser.add_argument("--num-fc", type=int, default=10, help='Number of fiscal codes to be generated')
    idpay_dataset_parser.add_argument("--min-pan-per-fc", type=int, default=1,
                                      help='Minimum number of payment instruments per fiscal code')
    idpay_dataset_parser.add_argument("--max-pan-per-fc", type=int, default=1,
                                      help='Maximum number of payment instruments per fiscal code')
    idpay_dataset_parser.add_argument("--trx-per-fc", type=int, default=1,
                                      help='Number of transactions per fiscal code')
    idpay_dataset_parser.add_argument("--sender-code", type=str, default='IDPAY',
                                      help='Sender code that will appear in transactions file')
    idpay_dataset_parser.add_argument("--acquirer-code", type=str, default='IDPAY',
                                      help='Acquirer code that will appear in transactions file')
    idpay_dataset_parser.add_argument("--start-datetime", type=str, default='2023-01-01T00:00:00.000+01:00',
                                      help='Lower bound of date and time in format yyyy-MM-ddTHH:mm:ss.SSSz of every transactions')
    idpay_dataset_parser.add_argument("--end-datetime", type=str,
                                      help='Upper bound of date and time in format yyyy-MM-ddTHH:mm:ss.SSSz of every transactions')
    idpay_dataset_parser.add_argument("--min-amount", type=int, default=1,
                                      help='Minimum amount of euro cents of a single transaction')
    idpay_dataset_parser.add_argument("--max-amount", type=int, default=1000,
                                      help='Maximum amount of euro cents of a single transaction')
    idpay_dataset_parser.add_argument("--mcc", type=str, default='1234',
                                      help='Merchant category code used in every transaction')
    idpay_dataset_parser.add_argument("--out-dir", type=str, default='./generated',
                                      help='Output destination of files generated')
    idpay_dataset_parser.add_argument("--env", type=str, choices=['dev', 'uat', 'prod'], default="dev",
                                      help='Environment')
    idpay_dataset_parser.add_argument("--api-key", type=str, default="aaa",
                                      help='API key capable of using RTD_API_Product')
    idpay_dataset_parser.add_argument("--key", type=str, default="~/certificates/private.key", required=False,
                                      help='Private key of the RTD mutual authentication certificate')
    idpay_dataset_parser.add_argument("--cert", type=str, default="~/certificates/public.key", required=False,
                                      help='Public key of the RTD mutual authentication certificate')
    idpay_dataset_parser.add_argument("--PM-pubk", type=str, default="./PM-public.asc", required=False,
                                      help='Path to the public key of the Payment Manager')
    idpay_dataset_parser.add_argument("--PM-salt", type=str, required=False,
                                      help='Current salt of the Payment Manager, if not specified the API is called')
    idpay_dataset_parser.add_argument("--RTD-pubk", type=str,
                                      help='Path to the public key of the RTD, if not specified the API is called')
    idpay_dataset_parser.add_argument("--IBAN-ABI", type=str, default='00001',
                                      help='ABI code used to generate test IBANs')
    idpay_dataset_parser.add_argument("--pdv-rate-limit", type=int, default=250,
                                      help="Request per second for PDV calls")
    idpay_dataset_parser.add_argument("--acquirer-id", type=str, default='PAGOPA',
                                      help='Acquirer ID through which the merchants will be uploaded')

    # -Rewards
    idpay_reward_parser = idpay_parser.add_parser("idpayrewards")
    idpay_reward_parser.add_argument("--action", required=True,
                                     help="Action to perform with the invocation of the command")
    idpay_reward_parser.add_argument("--payment-provisions-export", type=str, default="./payment-provisions.csv",
                                     help='Path to input payment provisions exported by IDPay')
    idpay_reward_parser.add_argument("--exec-date", type=str, default='2023-01-01',
                                     help='Date in format yyyy-MM-dd of reward process')
    idpay_reward_parser.add_argument("--perc-succ", type=float, default=0.1,
                                     help='Percentage of successful rewards')
    idpay_reward_parser.add_argument("--perc-dupl", type=float, default=0.1,
                                     help='Percentage of duplicates records')
    idpay_reward_parser.add_argument("--out-dir", type=str, default='./generated',
                                     help='Output destination of files generated')

    # -Transactions
    idpay_transactions_parser = idpay_parser.add_parser("idpaytransactions")
    idpay_transactions_parser.add_argument("--action", required=True,
                                           help="Action to perform with the invocation of the command")
    idpay_transactions_parser.add_argument("--trx-qty", type=int, default=1, help="Number of transactions desired")
    idpay_transactions_parser.add_argument("--sender-code", type=str, default='IDPAY',
                                           help='Sender code that will appear in transactions file')
    idpay_transactions_parser.add_argument("--acquirer-code", type=str, default='IDPAY',
                                           help='Acquirer code that will appear in transactions file')
    idpay_transactions_parser.add_argument("--start-datetime", type=str, default='2023-01-01T00:00:00.000+01:00',
                                           help='Lower bound of date and time in format yyyy-MM-ddTHH:mm:ss.SSSz of every transactions')
    idpay_transactions_parser.add_argument("--end-datetime", type=str,
                                           help='Upper bound of date and time in format yyyy-MM-ddTHH:mm:ss.SSSz of every transactions')
    idpay_transactions_parser.add_argument("--min-amount", type=int, default=1,
                                           help='Minimum amount of euro cents of a single transaction')
    idpay_transactions_parser.add_argument("--max-amount", type=int, default=1000,
                                           help='Maximum amount of euro cents of a single transaction')
    idpay_transactions_parser.add_argument("--mcc", type=str, default='1234',
                                           help='Merchant category code used in every transaction')
    idpay_transactions_parser.add_argument("--out-dir", type=str, default='./generated',
                                           help='Output destination of files generated')
    idpay_transactions_parser.add_argument("--env", type=str, choices=['dev', 'uat', 'prod'], default="dev",
                                           required=True,
                                           help='Environment')
    idpay_transactions_parser.add_argument("--api-key", type=str, default="aaa", required=True,
                                           help='API key capable of using RTD_API_Product')
    idpay_transactions_parser.add_argument("--key", type=str, default="~/certificates/private.key", required=True,
                                           help='Private key of the mutual authentication certificate')
    idpay_transactions_parser.add_argument("--cert", type=str, default="~/certificates/public.key", required=True,
                                           help='Public key of the mutual authentication certificate')
    idpay_transactions_parser.add_argument("--input-pans-hashpans", type=str,
                                           help="Path of pans-hashpans couples file used as payment methods in transactions' file")
    idpay_transactions_parser.add_argument("--input-hashpans-amounts", type=str,
                                           help="Path of hashpans-amounts couples file used as payment methods in transactions' file")
    idpay_transactions_parser.add_argument("--hpans-head", type=int, help="Takes the first N HPANs from HPANs file")
    idpay_transactions_parser.add_argument("--RTD-pubk", type=str,
                                           help='Path to the public key of the RTD, if not specified the API is called')

    wallet_parser = subsystem_parser.add_parser("wallet").add_subparsers(dest="command")

    wallet_argument_parser = wallet_parser.add_parser("contracts")

    # This will be used to call the methods through CLI
    wallet_argument_parser.add_argument("--action", required=True,
                                        help="Action to perform with the invocation of the command")
    wallet_argument_parser.add_argument("--contracts-qty", type=int, default=1, help="Number of contracts desired")
    wallet_argument_parser.add_argument("--out-dir", type=str, default='./generated',
                                        help='Output destination of file generated')
    wallet_argument_parser.add_argument("--pgp", action="store_true")
    wallet_argument_parser.add_argument("--key", type=str, default="./public.key")
    wallet_argument_parser.add_argument("--ratio-delete-contract", type=int, default=10)
    wallet_argument_parser.add_argument("--ratio-ko-delete-contract", type=int, default=5)


    return argparser
