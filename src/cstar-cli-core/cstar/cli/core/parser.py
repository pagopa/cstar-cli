import argparse

def parser():

    argparser = argparse.ArgumentParser()
    subsystem_parser = argparser.add_subparsers(dest="subsystem")
    subsystem_parser.required = True

    subsystem_parser.add_parser("fa")

    # FA commands
    # fa_parser.add_argument("intermediate")
    # fa_parser.add_argument("pem-csr-file", type=argparse.FileType('r'))
    # fa_parser.add_argument("--ttl", metavar="ttl")
    # fa_parser.add_argument("--send-email", action="store_true")
    # fa_parser.add_argument("--no-confirm", action="store_true")
    #sign_parser.set_defaults(call=client_sign)

    bpd_parser = subsystem_parser.add_parser("bpd").add_subparsers(dest="command")


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

    bpd_award_period = bpd_parser.add_parser("awardperiod")

    bpd_award_period.add_argument("--action")
    bpd_award_period.add_argument("--id")
    bpd_award_period.add_argument("--connection-string")


    #revoke_parser.set_defaults(call=client_revoke)

    return argparser



