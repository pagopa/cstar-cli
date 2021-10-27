import sys
from cstar.cli.core.parser import parser
import importlib


def main (args) :
  transaction_module = importlib.import_module("cstar.cli.bpd.%s" % (args.command))
  transaction_module.__getattribute__(args.command.lower().capitalize())(args).run()

if __name__ == '__main__':
    try:
        main(parser().parse_args())
    except KeyboardInterrupt:
        print("\n\n... goodbye!", file=sys.stderr)