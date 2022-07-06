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
    rtd_transaction_filter.add_argument("--sender", default=99999)
    rtd_transaction_filter.add_argument("--pans-prefix")
    rtd_transaction_filter.add_argument("--pans-qty", type=int)
    rtd_transaction_filter.add_argument("--hashpans-qty", type=int)
    rtd_transaction_filter.add_argument("--trx-qty", type=int)
    rtd_transaction_filter.add_argument("--ratio", type=int)
    rtd_transaction_filter.add_argument("--pos-number", type=int)
    rtd_transaction_filter.add_argument("--pgp", action="store_true")
    rtd_transaction_filter.add_argument("-o", "--out-dir", type=str, default=".")
    rtd_transaction_filter.add_argument("--key", type=str, default="./public.key")

    # TAE
    tae_parser = subsystem_parser.add_parser("tae").add_subparsers(dest="command")

    # -TRANSACTION AGGREGATE
    tae_transaction_aggregates = tae_parser.add_parser("transactionaggregate")

    tae_transaction_aggregates.add_argument("--action")
    tae_transaction_aggregates.add_argument("--aggr-qty", type=int)
    tae_transaction_aggregates.add_argument("--sender", default=99999)
    tae_transaction_aggregates.add_argument("--reverse-ratio", type=int)
    tae_transaction_aggregates.add_argument("-o", "--out-dir", type=str, default=".")
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
    tae_results.add_argument("-o", "--out-dir", type=str, default=".")
    tae_results.add_argument("--gzip", action="store_true")

    # -REPORTS
    tae_reports = tae_parser.add_parser("registryreports")

    tae_reports.add_argument("--action")
    tae_reports.add_argument("--rep-qty", type=int)
    tae_reports.add_argument("--acquirer", default=99999)
    tae_reports.add_argument("-o", "--out-dir", type=str, default=".")

    # SENDER
    sender_parser = subsystem_parser.add_parser("sender").add_subparsers(dest="command")

    # -AGGREGATES
    sender_aggregates_parser = sender_parser.add_parser("aggregates")

    sender_aggregates_parser.add_argument("--action", required=True,
                                          help="Action to perform with the invocation of the command")
    sender_aggregates_parser.add_argument("--aggr-qty", type=int, help="Aggregates quantity to generate")
    sender_aggregates_parser.add_argument("--sender", default=99999, help="Sender code")
    sender_aggregates_parser.add_argument("--avg-trx", type=int, default=10,
                                          help="Average transaction number per aggregation")
    sender_aggregates_parser.add_argument("-o", "--out-dir", type=str, default=".",
                                          help="Output directory of both files")
    sender_aggregates_parser.add_argument("--shuffle", action="store_true", help="Flag for shuffling transactions file")

    # -DIFF CHECKER
    sender_aggregates_parser.add_argument('-f', '--files', nargs=2, help="Files to compare for equality")

    return argparser
