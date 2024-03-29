import asyncio
import importlib
import sys

from cstar.cli.core.parser import parser


async def main(args):
    module = importlib.import_module(".%s" % args.subsystem.lower(), "cstar.cli")
    command_manager = module.__getattribute__(args.command.lower().capitalize())(args)
    action = command_manager.__getattribute__(args.action.lower())()
    if asyncio.iscoroutine(action):
        await action


if __name__ == '__main__':
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main(parser().parse_args()))
    except KeyboardInterrupt:
        print("\n\n... goodbye!", file=sys.stderr)
