import sys
from cstar.cli.core.parser import parser
import importlib

def main (args) :
  module = importlib.import_module( ".%s" % args.subsystem.lower(), "cstar.cli")
  command_manager = module.__getattribute__(args.command.lower().capitalize())(args)
  command_manager.__getattribute__(args.action.lower())()

if __name__ == '__main__':
    try:
        main(parser().parse_args())
    except KeyboardInterrupt:
        print("\n\n... goodbye!", file=sys.stderr)